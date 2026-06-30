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


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# GET â€” verificaciÃ³n del webhook Meta
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# POST â€” recibe mensajes entrantes de WhatsApp
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    3. Clasificar intenciÃ³n (IA)
    4. Ejecutar acciÃ³n (backend real)
    5. Construir respuesta (IA)
    6. Enviar por WhatsApp
    """
    body = await request.json()
    media_label = ""  # prefijo para el inbound Message guardado en DB

    # â”€â”€ Buscar negocio â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    stmt = select(Business).where(
        Business.phone_number_id == phone_number_id,
        Business.is_active == True,
    )
    result = await db.execute(stmt)
    business = result.scalar_one_or_none()

    if not business:
        logger.warning(f"phone_number_id no registrado: {phone_number_id}")
        return {"status": "business_not_found"}

    # â”€â”€ Parsear payload WhatsApp â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
                    "ðŸŽ™ï¸ No pude entender tu mensaje de voz. Â¿Puedes escribir tu consulta? ðŸ˜Š"
                )
                return {"status": "audio_transcription_failed"}
            message_text = transcribed
            media_label = "ðŸŽ™ï¸ "

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
                    "ðŸ–¼ï¸ RecibÃ­ tu imagen pero no pude interpretarla. Â¿Puedes describirme quÃ© necesitas?"
                )
                return {"status": "image_analysis_failed"}
            message_text = f"{caption} {img_desc}".strip() if caption else img_desc or caption
            media_label = "ðŸ–¼ï¸ "

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
                    "ðŸ“„ RecibÃ­ tu PDF pero no pude extraer el texto. Â¿Puedes describirme quÃ© necesitas?"
                )
                return {"status": "pdf_empty"}
            message_text = pdf_text
            media_label = "ðŸ“„ "

        else:
            return {"status": "unsupported_message_type"}

    except (KeyError, IndexError, TypeError) as exc:
        logger.error(f"Error parseando payload WhatsApp: {exc} | body={body}")
        return {"status": "parse_error"}

    # â”€â”€ Marcar como leÃ­do (no bloqueante) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    await mark_as_read(business.whatsapp_token, phone_number_id, wa_message_id)

    # â”€â”€ Obtener/crear conversaciÃ³n â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        logger.info(f"Nueva conversaciÃ³n: {conversation.id} con {customer_phone}")
    else:
        if customer_name and not conversation.customer_name:
            conversation.customer_name = customer_name

    # â”€â”€ Si estÃ¡ en handoff, no tocar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if conversation.status == ConversationStatus.HUMAN_HANDOFF:
        logger.info(f"ConversaciÃ³n {conversation.id} en handoff â€” ignorando mensaje")
        return {"status": "human_handoff_active"}

    # â”€â”€ Contexto del negocio para la IA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    cat_stmt = select(LegalCategory.name).where(
        LegalCategory.business_id == business.id,
        LegalCategory.is_active == True,
    )
    cat_result = await db.execute(cat_stmt)
    category_names = [row[0] for row in cat_result.all()]

    history: list = (conversation.context or {}).get("history", [])

    # â”€â”€ PASO 1: Clasificar intenciÃ³n â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    extracted = await classify_intent(
        message=message_text,
        business_name=business.name,
        business_type=business.business_type.value if business.business_type else "general",
        categories=category_names,
        conversation_history=history,
    )
    intent = extracted.intent

    # â”€â”€ Registrar lead (solo primera vez) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    # â”€â”€ Guardar mensaje entrante â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    db.add(Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        direction="inbound",
        content=f"{media_label}{message_text}" if media_label else message_text,
        intent=intent.value,
        wa_message_id=wa_message_id,
    ))

    # â”€â”€ PASO 2: Router de acciones â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    # â”€â”€ PASO 3: Construir y enviar respuesta â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

    logger.info(f"[{business.name}] {customer_phone} â†’ {intent.value}")
    return {"status": "ok", "intent": intent.value}


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Intent Router â€” Day 1 + Day 2
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

