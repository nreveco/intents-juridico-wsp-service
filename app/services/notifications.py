"""
notifications.py — Notifica al dueño del negocio vía WhatsApp cuando ocurre un evento clave.

Eventos:
- Nuevo pedido
- Nuevo carrito confirmado (checkout)
- Nueva reserva
- Nuevo lead
- Handoff solicitado
- Nueva cotización solicitada
"""
import logging
from typing import Optional

from app.whatsapp.gateway import send_text_message

logger = logging.getLogger(__name__)


async def notify_new_order(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    order_id: str,
    customer_phone: str,
    customer_name: str,
    product: str,
    quantity: int,
    total: float,
    currency_symbol: str = "$",
) -> None:
    msg = (
        f"🛒 *Nuevo Pedido #{order_id}*\n"
        f"• Cliente: {customer_name or customer_phone}\n"
        f"• Producto: {product} x{quantity}\n"
        f"• Total: {currency_symbol}{total:,.0f}\n"
        f"• Estado: Pendiente ⏳\n\n"
        f"Responde este mensaje para contactar al cliente."
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def notify_cart_checkout(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    order_id: str,
    customer_phone: str,
    customer_name: str,
    cart: list,
    total: float,
    currency_symbol: str = "$",
) -> None:
    items_text = "\n".join(
        f"  • {item['product_name']} x{item['quantity']} ({currency_symbol}{item['unit_price'] * item['quantity']:,.0f})"
        for item in cart
    )
    msg = (
        f"🛒 *Nuevo Pedido #{order_id}* (Carrito)\n"
        f"• Cliente: {customer_name or customer_phone}\n"
        f"• Ítems:\n{items_text}\n"
        f"• *Total: {currency_symbol}{total:,.0f}*\n"
        f"• Estado: Pendiente ⏳"
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def notify_new_booking(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    booking_id: str,
    customer_phone: str,
    customer_name: str,
    service: str,
    datetime_requested: str,
) -> None:
    msg = (
        f"📅 *Nueva Reserva #{booking_id}*\n"
        f"• Cliente: {customer_name or customer_phone} ({customer_phone})\n"
        f"• Servicio: {service}\n"
        f"• Cuando: {datetime_requested}\n\n"
        f"Confirma o cancela desde el panel admin."
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def notify_new_quote(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    quote_id: str,
    customer_phone: str,
    customer_name: str,
    description: str,
) -> None:
    msg = (
        f"📋 *Solicitud de Cotización #{quote_id}*\n"
        f"• Cliente: {customer_name or customer_phone} ({customer_phone})\n"
        f"• Solicita: {description}\n\n"
        f"Ingresa al panel admin para completar el presupuesto."
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def notify_handoff(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    customer_phone: str,
    customer_name: str,
    last_message: str,
) -> None:
    msg = (
        f"🔔 *Atención requerida*\n"
        f"• Cliente: {customer_name or customer_phone} ({customer_phone})\n"
        f"• Último mensaje: \"{last_message[:120]}\"\n\n"
        f"El cliente solicita hablar con un agente. Respóndele directamente."
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def notify_new_lead(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    customer_phone: str,
    customer_name: str,
    first_intent: str,
) -> None:
    msg = (
        f"👤 *Nuevo Lead*\n"
        f"• Teléfono: {customer_phone}\n"
        f"• Nombre: {customer_name or '—'}\n"
        f"• Primera consulta: {first_intent}"
    )
    await _notify(whatsapp_token, phone_number_id, owner_phone, msg)


async def _notify(
    whatsapp_token: str,
    phone_number_id: str,
    owner_phone: str,
    message: str,
) -> None:
    if not owner_phone:
        return
    try:
        await send_text_message(whatsapp_token, phone_number_id, owner_phone, message)
        logger.info(f"Notificación enviada al dueño ({owner_phone})")
    except Exception as exc:
        logger.warning(f"Error enviando notificación al dueño: {exc}")
