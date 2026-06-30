import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.intent_classifier import classify_intent
from app.ai.response_builder import build_response
from app.config import settings
from app.db.database import get_db
from app.db.models import (
    Business,
    BusinessSettings,
    LegalCategory,
    Conversation,
    ConversationStatus,
    Message,
)
from app.intents.definitions import Intent
from app.services import bookings, handoff, leads, notifications, quotes
from app.services import legal_services, case_inquiries, fee_info
from app.ai.media_processor import analyze_image, extract_pdf_text, transcribe_audio
from app.whatsapp.gateway import mark_as_read, send_text_message
from app.whatsapp.media import download_media

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhook", tags=["webhook"])


# ──────────────────────────────────────────────────────────────
# GET — verificación del webhook Meta
# ──────────────────────────────────────────────────────────────

@router.get("/{phone_number_id}")
async def verify_webhook(
    phone_number_id: str,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Meta llama a esta URL para verificar el webhook.
    Retorna el challenge si el token coincide.
    """
    if hub_mode == "subscribe" and hub_challenge:
        if hub_verify_token == settings.whatsapp_verify_token:
            logger.info(f"Webhook verificado para phone_number_id={phone_number_id}")
            return int(hub_challenge)
        raise HTTPException(status_code=403, detail="Invalid verify token")

    raise HTTPException(status_code=400, detail="Missing hub parameters")


# ──────────────────────────────────────────────────────────────
# POST — recibe mensajes entrantes de WhatsApp
# ──────────────────────────────────────────────────────────────

@router.post("/{phone_number_id}")
async def receive_message(
    phone_number_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Pipeline principal:
    1. Parsear payload Meta
    2. Buscar negocio en DB
    3. Clasificar intención (IA)
    4. Ejecutar acción (backend real)
    5. Construir respuesta (IA)
    6. Enviar por WhatsApp
    """
    body = await request.json()
    media_label = ""  # prefijo para el inbound Message guardado en DB

    # ── Buscar negocio ──────────────────────────────────────────
    stmt = select(Business).where(
        Business.phone_number_id == phone_number_id,
        Business.is_active == True,
    )
    result = await db.execute(stmt)
    business = result.scalar_one_or_none()

    if not business:
        logger.warning(f"phone_number_id no registrado: {phone_number_id}")
        return {"status": "business_not_found"}

    # ── Parsear payload WhatsApp ────────────────────────────────
    try:
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages_list = value.get("messages", [])

        if not messages_list:
            return {"status": "no_messages"}

        wa_message = messages_list[0]

        wa_message_type = wa_message.get("type")
        customer_phone: str = wa_message["from"]
        wa_message_id: str = wa_message["id"]

        contacts = value.get("contacts", [])
        customer_name = contacts[0].get("profile", {}).get("name", "") if contacts else ""

        if wa_message_type == "text":
            message_text = wa_message["text"]["body"].strip()

        elif wa_message_type == "interactive":
            inter = wa_message.get("interactive", {})
            if inter.get("type") == "button_reply":
                message_text = inter["button_reply"].get("title", "")
            elif inter.get("type") == "list_reply":
                message_text = inter["list_reply"].get("title", "")
            else:
                return {"status": "unsupported_interactive_type"}

        elif wa_message_type == "audio":
            audio_id = wa_message["audio"]["id"]
            try:
                audio_bytes, audio_mime = await download_media(business.whatsapp_token, audio_id)
                transcribed = await transcribe_audio(audio_bytes, audio_mime)
            except Exception as exc:
                logger.warning(f"Error procesando audio {audio_id}: {exc}")
                transcribed = ""
            if not transcribed:
                await mark_as_read(business.whatsapp_token, phone_number_id, wa_message_id)
                await send_text_message(
                    business.whatsapp_token, phone_number_id, customer_phone,
                    "🎙️ No pude entender tu mensaje de voz. ¿Puedes escribir tu consulta? 😊"
                )
                return {"status": "audio_transcription_failed"}
            message_text = transcribed
            media_label = "🎙️ "

        elif wa_message_type == "image":
            img = wa_message["image"]
            caption = img.get("caption", "").strip()
            try:
                img_bytes, img_mime = await download_media(business.whatsapp_token, img["id"])
                img_desc = await analyze_image(img_bytes, img_mime, business.name)
            except Exception as exc:
                logger.warning(f"Error procesando imagen: {exc}")
                img_desc = ""
            if not img_desc and not caption:
                await send_text_message(
                    business.whatsapp_token, phone_number_id, customer_phone,
                    "🖼️ Recibí tu imagen pero no pude interpretarla. ¿Puedes describirme qué necesitas?"
                )
                return {"status": "image_analysis_failed"}
            message_text = f"{caption} {img_desc}".strip() if caption else img_desc or caption
            media_label = "🖼️ "

        elif wa_message_type == "document":
            doc = wa_message.get("document", {})
            doc_mime = doc.get("mime_type", "").lower()
            doc_filename = doc.get("filename", "").lower()
            if "pdf" not in doc_mime and not doc_filename.endswith(".pdf"):
                return {"status": "unsupported_document_type"}
            try:
                pdf_bytes, _ = await download_media(business.whatsapp_token, doc["id"])
                pdf_text = await extract_pdf_text(pdf_bytes)
            except Exception as exc:
                logger.warning(f"Error procesando PDF: {exc}")
                pdf_text = ""
            if not pdf_text.strip():
                await send_text_message(
                    business.whatsapp_token, phone_number_id, customer_phone,
                    "📄 Recibí tu PDF pero no pude extraer el texto. ¿Puedes describirme qué necesitas?"
                )
                return {"status": "pdf_empty"}
            message_text = pdf_text
            media_label = "📄 "

        else:
            return {"status": "unsupported_message_type"}

    except (KeyError, IndexError, TypeError) as exc:
        logger.error(f"Error parseando payload WhatsApp: {exc} | body={body}")
        return {"status": "parse_error"}

    # ── Marcar como leído (no bloqueante) ───────────────────────
    await mark_as_read(business.whatsapp_token, phone_number_id, wa_message_id)

    # ── Obtener/crear conversación ──────────────────────────────
    conv_stmt = select(Conversation).where(
        Conversation.business_id == business.id,
        Conversation.customer_phone == customer_phone,
        Conversation.status == ConversationStatus.ACTIVE,
    )
    conv_result = await db.execute(conv_stmt)
    conversation = conv_result.scalar_one_or_none()

    is_new_conversation = False
    if not conversation:
        conversation = Conversation(
            id=str(uuid.uuid4()),
            business_id=business.id,
            customer_phone=customer_phone,
            customer_name=customer_name,
            status=ConversationStatus.ACTIVE,
            context={"history": [], "cart": []},
        )
        db.add(conversation)
        await db.flush()
        is_new_conversation = True
        logger.info(f"Nueva conversación: {conversation.id} con {customer_phone}")
    else:
        if customer_name and not conversation.customer_name:
            conversation.customer_name = customer_name

    # ── Si está en handoff, no tocar ────────────────────────────
    if conversation.status == ConversationStatus.HUMAN_HANDOFF:
        logger.info(f"Conversación {conversation.id} en handoff — ignorando mensaje")
        return {"status": "human_handoff_active"}

    # ── Contexto del negocio para la IA ──────────────────────────
    cat_stmt = select(LegalCategory.name).where(
        LegalCategory.business_id == business.id,
        LegalCategory.is_active == True,
    )
    cat_result = await db.execute(cat_stmt)
    category_names = [row[0] for row in cat_result.all()]

    history: list = (conversation.context or {}).get("history", [])

    # ── PASO 1: Clasificar intención ────────────────────────────
    extracted = await classify_intent(
        message=message_text,
        business_name=business.name,
        business_type=business.business_type.value if business.business_type else "general",
        categories=category_names,
        conversation_history=history,
    )
    intent = extracted.intent

    # ── Registrar lead (solo primera vez) ───────────────────────
    if is_new_conversation:
        await leads.register_lead(
            db, business.id, customer_phone, name=customer_name, intent=intent.value
        )
        if business.human_support_phone:
            await notifications.notify_new_lead(
                whatsapp_token=business.whatsapp_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                customer_phone=customer_phone,
                customer_name=customer_name,
                first_intent=intent.value,
            )

    # ── Guardar mensaje entrante ────────────────────────────────
    db.add(Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        direction="inbound",
        content=f"{media_label}{message_text}" if media_label else message_text,
        intent=intent.value,
        wa_message_id=wa_message_id,
    ))

    # ── PASO 2: Router de acciones ──────────────────────────────
    settings_stmt = select(BusinessSettings).where(BusinessSettings.business_id == business.id)
    settings_result = await db.execute(settings_stmt)
    biz_settings = settings_result.scalar_one_or_none()
    currency_symbol = biz_settings.currency_symbol if biz_settings else "$"

    query_result, interactive_sent = await _route_intent(
        intent=intent,
        extracted=extracted,
        business=business,
        biz_settings=biz_settings,
        db=db,
        customer_phone=customer_phone,
        customer_name=customer_name,
        conversation=conversation,
        currency_symbol=currency_symbol,
        phone_number_id=phone_number_id,
        message_text=message_text,
    )

    # ── PASO 3: Construir y enviar respuesta ────────────────────
    if not interactive_sent:
        if query_result.get("default_message") and not query_result.get("data"):
            response_text = query_result["default_message"]
        else:
            response_text = await build_response(
                intent=intent.value,
                original_message=message_text,
                query_result=query_result,
                business_name=business.name,
                currency_symbol=currency_symbol,
            )

        db.add(Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            direction="outbound",
            content=response_text,
            intent=intent.value,
        ))

        history.append({"role": "user", "content": message_text})
        history.append({"role": "assistant", "content": response_text})
        ctx = dict(conversation.context or {})
        ctx["history"] = history[-8:]
        conversation.context = ctx
        await db.commit()

        await send_text_message(
            whatsapp_token=business.whatsapp_token,
            phone_number_id=phone_number_id,
            to_phone=customer_phone,
            message=response_text,
        )
    else:
        history.append({"role": "user", "content": message_text})
        history.append({"role": "assistant", "content": "[interactive]"})
        ctx = dict(conversation.context or {})
        ctx["history"] = history[-8:]
        conversation.context = ctx
        await db.commit()

    logger.info(f"[{business.name}] {customer_phone} → {intent.value}")
    return {"status": "ok", "intent": intent.value}


# ──────────────────────────────────────────────────────────────
# Intent Router — Day 1 + Day 2
# ──────────────────────────────────────────────────────────────

async def _route_intent(
    intent: Intent,
    extracted,
    business: Business,
    biz_settings,
    db: AsyncSession,
    customer_phone: str,
    customer_name: str,
    conversation: Conversation,
    currency_symbol: str,
    phone_number_id: str,
    message_text: str,
) -> tuple[dict, bool]:
    """Retorna (query_result, interactive_sent)."""
    wa_token = business.whatsapp_token

    if intent == Intent.GREETING:
        sent = await send_welcome_buttons(
            whatsapp_token=wa_token,
            phone_number_id=phone_number_id,
            to_phone=customer_phone,
            business_name=business.name,
            custom_message=business.welcome_message,
        )
        if sent:
            return {}, True
        msg = business.welcome_message or (
            f"¡Hola! 👋 Bienvenido a *{business.name}*.\n"
            "Puedo ayudarte con precios, pedidos, reservas y más. ¿En qué te ayudo?"
        )
        return {"default_message": msg}, False

    elif intent == Intent.PRICE_QUERY:
        if extracted.product_name:
            return await products.find_product_by_name(db, business.id, extracted.product_name), False
        return {"default_message": "¿De qué producto o servicio te gustaría saber el precio? 😊"}, False

    elif intent == Intent.PRODUCT_INFO:
        if extracted.product_name:
            return await products.find_product_by_name(db, business.id, extracted.product_name), False
        menu = await products.get_menu_by_category(db, business.id)
        if menu.get("found") and menu.get("data"):
            sent = await send_catalog_list(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                to_phone=customer_phone,
                grouped_products=menu["data"],
                currency_symbol=currency_symbol,
            )
            if sent:
                return {}, True
        return menu, False

    elif intent == Intent.ORDER_CREATE:
        if extracted.product_name:
            result = await orders.create_order(
                db=db,
                business_id=business.id,
                customer_phone=customer_phone,
                product_query=extracted.product_name,
                quantity=extracted.quantity or 1,
                customer_name=customer_name,
            )
            if result.get("success") and business.human_support_phone:
                data = result["data"]
                await notifications.notify_new_order(
                    whatsapp_token=wa_token,
                    phone_number_id=phone_number_id,
                    owner_phone=business.human_support_phone,
                    order_id=data["order_id"],
                    customer_phone=customer_phone,
                    customer_name=customer_name,
                    product=data["product"],
                    quantity=data["quantity"],
                    total=data["total"],
                    currency_symbol=currency_symbol,
                )
            return result, False
        return {"default_message": "¿Qué te gustaría pedir? Dime el nombre del producto. 🛒"}, False

    elif intent == Intent.ORDER_STATUS:
        return await orders.get_order_status(db, business.id, customer_phone), False

    elif intent == Intent.BOOKING:
        if extracted.datetime_requested:
            result = await bookings.create_booking(
                db=db,
                business_id=business.id,
                customer_phone=customer_phone,
                service=extracted.service or "reserva general",
                datetime_requested=extracted.datetime_requested,
                customer_name=customer_name,
            )
            if result.get("success") and business.human_support_phone:
                data = result["data"]
                await notifications.notify_new_booking(
                    whatsapp_token=wa_token,
                    phone_number_id=phone_number_id,
                    owner_phone=business.human_support_phone,
                    booking_id=data["booking_id"],
                    customer_phone=customer_phone,
                    customer_name=customer_name,
                    service=data["service"],
                    datetime_requested=data["datetime_requested"],
                )
            return result, False
        return {"default_message": "¿Para qué día y hora te gustaría reservar? 📅"}, False

    elif intent == Intent.QUOTE_REQUEST:
        description = (
            extracted.quote_description
            or extracted.service
            or extracted.product_name
            or message_text
        )
        result = await quotes.create_quote_request(
            db=db,
            business_id=business.id,
            customer_phone=customer_phone,
            description=description,
            customer_name=customer_name,
        )
        if result.get("success") and business.human_support_phone:
            data = result["data"]
            await notifications.notify_new_quote(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                quote_id=data["quote_id"],
                customer_phone=customer_phone,
                customer_name=customer_name,
                description=description,
            )
        return result, False

    elif intent == Intent.CART_ADD:
        if not extracted.product_name:
            return {"default_message": "¿Qué producto quieres agregar al pedido? 🛒"}, False
        result = await cart.add_to_cart(
            db=db,
            conversation=conversation,
            business_id=business.id,
            product_query=extracted.product_name,
            quantity=extracted.quantity or 1,
        )
        if not result.get("success"):
            return result, False
        data = result["data"]
        cart_text = cart.format_cart_text(data["cart"], currency_symbol)
        sent = await send_order_confirmation_buttons(
            whatsapp_token=wa_token,
            phone_number_id=phone_number_id,
            to_phone=customer_phone,
            cart_summary=cart_text,
            total=data["cart_total"],
            currency_symbol=currency_symbol,
        )
        if sent:
            return {}, True
        return {
            "data": data,
            "default_message": (
                f"✅ *{data['product']}* x{data['quantity']} agregado.\n\n"
                f"{cart_text}\n\n"
                "¿Quieres agregar algo más o confirmar el pedido?"
            ),
        }, False

    elif intent == Intent.CART_VIEW:
        result = cart.view_cart(conversation, currency_symbol)
        if not result.get("success"):
            return result, False
        data = result["data"]
        cart_text = cart.format_cart_text(data["cart"], currency_symbol)
        sent = await send_order_confirmation_buttons(
            whatsapp_token=wa_token,
            phone_number_id=phone_number_id,
            to_phone=customer_phone,
            cart_summary=cart_text,
            total=data["total"],
            currency_symbol=currency_symbol,
        )
        if sent:
            return {}, True
        return {"data": data, "default_message": f"*Tu carrito:*\n\n{cart_text}"}, False

    elif intent == Intent.CART_CHECKOUT:
        result = await cart.checkout_cart(
            db=db,
            conversation=conversation,
            business_id=business.id,
            customer_phone=customer_phone,
            customer_name=customer_name,
        )
        if result.get("success") and business.human_support_phone:
            data = result["data"]
            await notifications.notify_cart_checkout(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                order_id=data["order_id"],
                customer_phone=customer_phone,
                customer_name=customer_name,
                cart=data["items"],
                total=data["total"],
                currency_symbol=currency_symbol,
            )
        return result, False

    elif intent == Intent.CART_CLEAR:
        return cart.clear_cart(conversation), False

    elif intent == Intent.HOURS_QUERY:
        if biz_settings and biz_settings.hours:
            return {"data": {"horarios": biz_settings.hours}}, False
        return {"default_message": "Para consultar nuestros horarios escríbenos aquí. 🕐"}, False

    elif intent == Intent.LOCATION_QUERY:
        if biz_settings and biz_settings.address:
            msg = f"📍 *Dirección:* {biz_settings.address}"
            if biz_settings.city:
                msg += f", {biz_settings.city}"
            if biz_settings.maps_url:
                msg += f"\n🗺️ Google Maps: {biz_settings.maps_url}"
            return {"data": {"address": biz_settings.address}, "default_message": msg}, False
        return {"default_message": "📍 Escríbenos y te enviamos la ubicación exacta. ¡Te esperamos!"}, False

    elif intent == Intent.HUMAN_SUPPORT:
        result = await handoff.request_human_handoff(
            db=db,
            conversation_id=conversation.id,
            human_support_phone=business.human_support_phone or "",
        )
        if business.human_support_phone:
            await notifications.notify_handoff(
                whatsapp_token=wa_token,
                phone_number_id=phone_number_id,
                owner_phone=business.human_support_phone,
                customer_phone=customer_phone,
                customer_name=customer_name,
                last_message=message_text,
            )
        return result, False

    else:
        return {
            "default_message": (
                "No entendí bien tu consulta 🤔 Puedo ayudarte con:\n"
                "• 💰 Precios y productos\n"
                "• 🛒 Hacer un pedido\n"
                "• 📅 Reservas y cotizaciones\n"
                "• 🕐 Horarios y ubicación\n"
                "• 👨‍💼 Hablar con una persona\n\n"
                "¿Qué necesitas?"
            )
        }, False


def _map_button_id(btn_id: str) -> str:
    mapping = {
        "action_menu": "quiero ver el menú",
        "action_order": "quiero hacer un pedido",
        "action_booking": "quiero reservar",
        "confirm_order": "confirmar pedido",
        "add_more": "quiero agregar más cosas al pedido",
        "cancel_order": "cancelar mi pedido",
    }
    return mapping.get(btn_id, btn_id.replace("_", " "))
