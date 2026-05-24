import logging

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


async def send_text_message(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    message: str,
) -> bool:
    """Envía un mensaje de texto simple vía Meta Cloud API."""
    url = GRAPH_API_URL.format(phone_number_id=phone_number_id)

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": message},
    }

    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                logger.info(f"Mensaje enviado a {to_phone}")
                return True
            else:
                logger.error(
                    f"Error enviando mensaje a {to_phone}: "
                    f"{response.status_code} {response.text}"
                )
                return False
    except Exception as exc:
        logger.error(f"Excepción al enviar mensaje WhatsApp: {exc}")
        return False


async def mark_as_read(
    whatsapp_token: str,
    phone_number_id: str,
    wa_message_id: str,
) -> None:
    """Marca el mensaje entrante como leído (doble palomita azul)."""
    url = GRAPH_API_URL.format(phone_number_id=phone_number_id)

    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": wa_message_id,
    }

    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(url, json=payload, headers=headers)
    except Exception:
        pass  # No crítico si falla
