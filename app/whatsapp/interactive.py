"""
interactive.py — Mensajes interactivos de WhatsApp vía Meta Cloud API.

Tipos soportados:
- Botones de respuesta rápida (hasta 3 botones)
- Mensajes de lista (hasta 10 secciones, 10 ítems cada una)

Útil para:
- Menú de bienvenida con botones
- Catálogo de productos por categoría
- Confirmaciones de pedido
"""
import logging

import httpx

logger = logging.getLogger(__name__)

GRAPH_API_URL = "https://graph.facebook.com/v19.0/{phone_number_id}/messages"


async def send_button_message(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    body_text: str,
    buttons: list[dict],
    header_text: str | None = None,
    footer_text: str | None = None,
) -> bool:
    """
    Envía un mensaje con botones de respuesta rápida.

    buttons: lista de dicts con {"id": str, "title": str}
    Máximo 3 botones. Title máx 20 chars.
    """
    buttons_payload = [
        {
            "type": "reply",
            "reply": {"id": btn["id"], "title": btn["title"][:20]},
        }
        for btn in buttons[:3]
    ]

    interactive: dict = {
        "type": "button",
        "body": {"text": body_text},
        "action": {"buttons": buttons_payload},
    }

    if header_text:
        interactive["header"] = {"type": "text", "text": header_text[:60]}
    if footer_text:
        interactive["footer"] = {"text": footer_text[:60]}

    return await _send_interactive(whatsapp_token, phone_number_id, to_phone, interactive)


async def send_list_message(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    body_text: str,
    button_label: str,
    sections: list[dict],
    header_text: str | None = None,
    footer_text: str | None = None,
) -> bool:
    """
    Envía un mensaje de lista desplegable.

    sections: lista de dicts con {"title": str, "rows": [{"id": str, "title": str, "description": str}]}
    Máximo 10 secciones, 10 ítems por sección. Titles máx 24 chars.
    """
    clean_sections = []
    for section in sections[:10]:
        rows = [
            {
                "id": row["id"][:200],
                "title": row["title"][:24],
                "description": row.get("description", "")[:72],
            }
            for row in section.get("rows", [])[:10]
        ]
        if rows:
            clean_sections.append({"title": section["title"][:24], "rows": rows})

    interactive: dict = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_label[:20],
            "sections": clean_sections,
        },
    }

    if header_text:
        interactive["header"] = {"type": "text", "text": header_text[:60]}
    if footer_text:
        interactive["footer"] = {"text": footer_text[:60]}

    return await _send_interactive(whatsapp_token, phone_number_id, to_phone, interactive)


async def _send_interactive(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    interactive: dict,
) -> bool:
    url = GRAPH_API_URL.format(phone_number_id=phone_number_id)
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "interactive",
        "interactive": interactive,
    }
    headers = {
        "Authorization": f"Bearer {whatsapp_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                logger.info(f"Interactive message enviado a {to_phone}")
                return True
            logger.error(
                f"Error interactive message {to_phone}: {response.status_code} {response.text}"
            )
            return False
    except Exception as exc:
        logger.error(f"Excepción enviando interactive message: {exc}")
        return False


# ──────────────────────────────────────────────────────────────
# Builders predefinidos
# ──────────────────────────────────────────────────────────────

async def send_welcome_buttons(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    business_name: str,
    custom_message: str | None = None,
) -> bool:
    body = custom_message or (
        f"¡Bienvenido a *{business_name}*! 👋\n¿En qué te puedo ayudar hoy?"
    )
    return await send_button_message(
        whatsapp_token=whatsapp_token,
        phone_number_id=phone_number_id,
        to_phone=to_phone,
        body_text=body,
        buttons=[
            {"id": "action_menu", "title": "Ver Menú 🍽️"},
            {"id": "action_order", "title": "Hacer Pedido 🛒"},
            {"id": "action_booking", "title": "Reservar 📅"},
        ],
    )


async def send_catalog_list(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    grouped_products: dict[str, list],
    currency_symbol: str = "$",
) -> bool:
    """Envía el catálogo como lista interactiva agrupada por categoría."""
    sections = []
    for cat_name, items in grouped_products.items():
        rows = [
            {
                "id": f"product_{item.get('id', idx)}",
                "title": item["name"][:24],
                "description": f"{currency_symbol}{item['price']:,.0f}",
            }
            for idx, item in enumerate(items[:10])
        ]
        if rows:
            sections.append({"title": cat_name, "rows": rows})

    if not sections:
        return False

    return await send_list_message(
        whatsapp_token=whatsapp_token,
        phone_number_id=phone_number_id,
        to_phone=to_phone,
        header_text="Nuestro Menú 🍽️",
        body_text="Toca un producto para consultarnos precio o más detalles.",
        button_label="Ver opciones",
        sections=sections,
    )


async def send_order_confirmation_buttons(
    whatsapp_token: str,
    phone_number_id: str,
    to_phone: str,
    cart_summary: str,
    total: float,
    currency_symbol: str = "$",
) -> bool:
    body = (
        f"*Resumen de tu pedido:*\n"
        f"{cart_summary}\n\n"
        f"💰 *Total: {currency_symbol}{total:,.0f}*\n\n"
        f"¿Confirmamos tu pedido?"
    )
    return await send_button_message(
        whatsapp_token=whatsapp_token,
        phone_number_id=phone_number_id,
        to_phone=to_phone,
        body_text=body,
        buttons=[
            {"id": "confirm_order", "title": "✅ Confirmar"},
            {"id": "add_more", "title": "➕ Agregar más"},
            {"id": "cancel_order", "title": "❌ Cancelar"},
        ],
    )
