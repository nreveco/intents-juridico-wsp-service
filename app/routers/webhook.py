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
from app.routers.webhook_legal_route import _route_intent_legal
from app.services import handoff, leads, notifications
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
    media_label = ""  # prefijo para el inbound Message guardado en DB

    # ── Buscar negocio ──────────────────────────────────────────
    logger.info(
        "Lookup business for incoming webhook",
        extra={
            "phone_number_id": phone_number_id,
            "env_whatsapp_phone_number_id": settings.whatsapp_phone_number_id,
        },
    )

    stmt = select(Business).where(
        Business.phone_number_id == phone_number_id,
        Business.is_active == True,
    )
    result = await db.execute(stmt)
    business = result.scalar_one_or_none()

    if not business and settings.whatsapp_phone_number_id:
        logger.info(
            "Incoming phone_number_id not registered, falling back to env WHATSAPP_PHONE_NUMBER_ID",
            extra={
                "incoming_phone_number_id": phone_number_id,
                "fallback_phone_number_id": settings.whatsapp_phone_number_id,
            },
        )
        stmt = select(Business).where(
            Business.phone_number_id == settings.whatsapp_phone_number_id,
            Business.is_active == True,
        )
        result = await db.execute(stmt)
        business = result.scalar_one_or_none()

    if not business:
        active_stmt = select(Business.phone_number_id).where(Business.is_active == True)
        active_result = await db.execute(active_stmt)
        active_ids = [row[0] for row in active_result.all()]
        logger.warning(
            f"phone_number_id no registrado: {phone_number_id}. "
            f"Active phone_number_ids={active_ids}"
        )
        return {"status": "business_not_found"}

    logger.info(
        "Business found for webhook request",
        extra={
            "phone_number_id": phone_number_id,
            "business_id": business.id,
            "business_name": business.name,
        },
    )

    whatsapp_token = settings.whatsapp_token
    whatsapp_phone_number_id = settings.whatsapp_phone_number_id
    if not whatsapp_token or not whatsapp_phone_number_id:
        logger.error(
            "Faltan credenciales de WhatsApp en el archivo .env",
            extra={
                "whatsapp_token": bool(whatsapp_token),
                "whatsapp_phone_number_id": bool(whatsapp_phone_number_id),
            },
        )
        return {
            "status": "missing_whatsapp_env_credentials",
            "error": "Missing WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID",
        }

    # ── Parsear payload WhatsApp ────────────────────────────────
    try:
        body = await request.json()
    except Exception as exc:
        raw_body = (await request.body()).decode("utf-8", "replace")
        logger.error(
            "Error leyendo payload JSON del webhook",
            extra={
                "error": str(exc),
                "content_type": request.headers.get("content-type"),
                "body_snippet": raw_body[:200],
            },
        )
        return {
            "status": "invalid_json_payload",
            "error": str(exc),
        }

    try:
        logger.info("Parsing WhatsApp payload", extra={"body_keys": list(body.keys())})
        entry = body.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        messages_list = value.get("messages", [])

        if not messages_list:
            logger.warning(
                "Webhook payload contains no WhatsApp messages",
                extra={"payload_value": value},
            )
            return {"status": "no_messages"}

        wa_message = messages_list[0]

        wa_message_type = wa_message.get("type")
        customer_phone: str = wa_message["from"]
        wa_message_id: str = wa_message["id"]

        contacts = value.get("contacts", [])
        customer_name = contacts[0].get("profile", {}).get("name", "") if contacts else ""

        logger.info(
            "Parsed incoming WhatsApp message",
            extra={
                "phone_number_id": phone_number_id,
                "message_type": wa_message_type,
                "customer_phone": customer_phone,
                "customer_name": customer_name,
                "wa_message_id": wa_message_id,
            },
        )

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
                audio_bytes, audio_mime = await download_media(whatsapp_token, audio_id)
                transcribed = await transcribe_audio(audio_bytes, audio_mime)
            except Exception as exc:
                logger.warning(f"Error procesando audio {audio_id}: {exc}")
                transcribed = ""
            if not transcribed:
                await mark_as_read(whatsapp_token, whatsapp_phone_number_id, wa_message_id)
                await send_text_message(
                    whatsapp_token, whatsapp_phone_number_id, customer_phone,
                    "🎙️ No pude entender tu mensaje de voz. ¿Puedes escribir tu consulta? 😊"
                )
                return {"status": "audio_transcription_failed"}
            message_text = transcribed
            media_label = "🎙️ "

        elif wa_message_type == "image":
            img = wa_message["image"]
            caption = img.get("caption", "").strip()
            try:
                img_bytes, img_mime = await download_media(whatsapp_token, img["id"])
                img_desc = await analyze_image(img_bytes, img_mime, business.name)
            except Exception as exc:
                logger.warning(f"Error procesando imagen: {exc}")
                img_desc = ""
            if not img_desc and not caption:
                await send_text_message(
                    whatsapp_token, whatsapp_phone_number_id, customer_phone,
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
                pdf_bytes, _ = await download_media(whatsapp_token, doc["id"])
                pdf_text = await extract_pdf_text(pdf_bytes)
            except Exception as exc:
                logger.warning(f"Error procesando PDF: {exc}")
                pdf_text = ""
            if not pdf_text.strip():
                await send_text_message(
                    whatsapp_token, whatsapp_phone_number_id, customer_phone,
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

    # ── Verificar si el mensaje ya fue procesado (deduplicación) ──
    from sqlalchemy import exists
    
    # Usar select con exists es más eficiente
    stmt_check = select(exists().where(Message.wa_message_id == wa_message_id))
    result_check = await db.execute(stmt_check)
    message_exists = result_check.scalar()
    
    if message_exists:
        logger.info(f"Mensaje duplicado detectado: {wa_message_id} - ignorando")
        return {"status": "duplicate_message"}

    # ── Marcar como leído (no bloqueante) ───────────────────────
    await mark_as_read(whatsapp_token, whatsapp_phone_number_id, wa_message_id)

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

    logger.info(
        "Step 1: Media processed, handing off to intent classifier",
        extra={
            "phone_number_id": phone_number_id,
            "business_id": business.id,
            "message_text": message_text,
            "media_label": media_label,
        },
    )

    # ── PASO 1: Clasificar intención ────────────────────────────
    extracted = await classify_intent(
        message=message_text,
        business_name=business.name,
        business_type=business.business_type.value if business.business_type else "general",
        categories=category_names,
        conversation_history=history,
    )
    intent = extracted.intent
    logger.info(
        "Intent classification completed",
        extra={
            "intent": intent.value,
            "extracted_product": getattr(extracted, 'product_name', None),
            "extracted_entities": extracted.dict(exclude={'intent'}),
        },
    )

    # ── Registrar lead (solo primera vez) ───────────────────────
    if is_new_conversation:
        await leads.register_lead(
            db, business.id, customer_phone, name=customer_name, intent=intent.value
        )
        if business.human_support_phone:
            await notifications.notify_new_lead(
                whatsapp_token=whatsapp_token,
                phone_number_id=whatsapp_phone_number_id,
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

    query_result, interactive_sent = await _route_intent_legal(
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
    logger.info(
        "Step 2: Action router completed",
        extra={
            "intent": intent.value,
            "query_result": query_result,
            "interactive_sent": interactive_sent,
        },
    )

    # ── PASO 3: Construir y enviar respuesta ────────────────────
    if not interactive_sent:
        if query_result.get("default_message") and not query_result.get("data"):
            logger.info(
                "Step 4: Using default message from action router",
                extra={"query_result": query_result},
            )
            response_text = query_result["default_message"]
        else:
            logger.info(
                "Step 4: Building response from query result",
                extra={"query_result": query_result},
            )
            response_text = await build_response(
                intent=intent.value,
                original_message=message_text,
                query_result=query_result,
                business_name=business.name,
                currency_symbol=currency_symbol,
            )
            logger.info(
                "Response builder completed",
                extra={"response_text": response_text},
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
            whatsapp_token=whatsapp_token,
            phone_number_id=whatsapp_phone_number_id,
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
