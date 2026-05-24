"""
cart.py — Carrito multi-ítem almacenado en conversation.context["cart"]

Estructura del carrito en context:
{
  "cart": [
    {"product_id": "...", "product_name": "...", "unit_price": 2800.0, "quantity": 2},
    ...
  ]
}
"""
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Order, OrderItem, OrderStatus, Product

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# Cart helpers (pure, no DB needed)
# ──────────────────────────────────────────────────────────────

def get_cart(conversation: Conversation) -> list:
    return (conversation.context or {}).get("cart", [])


def cart_total(cart: list) -> float:
    return round(sum(item["unit_price"] * item["quantity"] for item in cart), 2)


def format_cart_text(cart: list, currency_symbol: str = "$") -> str:
    if not cart:
        return "Tu carrito está vacío. 🛒"
    lines = []
    for item in cart:
        subtotal = item["unit_price"] * item["quantity"]
        lines.append(
            f"• {item['product_name']} x{item['quantity']} — "
            f"{currency_symbol}{subtotal:,.0f}"
        )
    total = cart_total(cart)
    lines.append(f"\n*Total: {currency_symbol}{total:,.0f}*")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Cart operations (DB lookup for product validation)
# ──────────────────────────────────────────────────────────────

async def add_to_cart(
    db: AsyncSession,
    conversation: Conversation,
    business_id: str,
    product_query: str,
    quantity: int = 1,
) -> dict:
    """Busca el producto en DB y lo agrega al carrito de la conversación."""
    stmt = (
        select(Product)
        .where(
            Product.business_id == business_id,
            Product.is_available == True,
            Product.name.ilike(f"%{product_query}%"),
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    product = result.scalar_one_or_none()

    if not product:
        return {
            "success": False,
            "default_message": (
                f"No encontré *{product_query}* en nuestro catálogo. 🤔\n"
                "¿Podrías verificar el nombre?"
            ),
        }

    cart = get_cart(conversation)

    # Si ya existe, sumar cantidad
    for item in cart:
        if item["product_id"] == product.id:
            item["quantity"] += quantity
            _save_cart(conversation, cart)
            total = cart_total(cart)
            return {
                "success": True,
                "data": {
                    "product": product.name,
                    "quantity": item["quantity"],
                    "cart_total": total,
                    "cart": cart,
                },
            }

    cart.append({
        "product_id": product.id,
        "product_name": product.name,
        "unit_price": product.price,
        "quantity": quantity,
    })
    _save_cart(conversation, cart)
    total = cart_total(cart)

    logger.info(f"Carrito {conversation.id}: +{product.name} x{quantity}")

    return {
        "success": True,
        "data": {
            "product": product.name,
            "quantity": quantity,
            "cart_total": total,
            "cart": cart,
        },
    }


async def checkout_cart(
    db: AsyncSession,
    conversation: Conversation,
    business_id: str,
    customer_phone: str,
    customer_name: str = "",
) -> dict:
    """Convierte el carrito en una Order real en la DB."""
    cart = get_cart(conversation)

    if not cart:
        return {
            "success": False,
            "default_message": "Tu carrito está vacío. Primero agrégame los productos que quieres pedir. 🛒",
        }

    order_id = str(uuid.uuid4())
    total = cart_total(cart)

    order = Order(
        id=order_id,
        business_id=business_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        status=OrderStatus.PENDING,
        total=total,
    )
    db.add(order)

    for item in cart:
        db.add(OrderItem(
            id=str(uuid.uuid4()),
            order_id=order_id,
            product_id=item.get("product_id"),
            product_name=item["product_name"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
        ))

    # Limpiar carrito
    _save_cart(conversation, [])
    await db.commit()

    short_id = order_id[:8].upper()
    logger.info(f"Checkout completado: #{short_id} — total ${total}")

    return {
        "success": True,
        "data": {
            "order_id": short_id,
            "items": cart,
            "total": total,
            "status": "pendiente ⏳",
        },
    }


def view_cart(conversation: Conversation, currency_symbol: str = "$") -> dict:
    cart = get_cart(conversation)
    if not cart:
        return {
            "success": False,
            "default_message": "Tu carrito está vacío. 🛒 ¿Qué te gustaría pedir?",
        }
    return {
        "success": True,
        "data": {
            "cart": cart,
            "total": cart_total(cart),
            "items_count": sum(i["quantity"] for i in cart),
        },
    }


def clear_cart(conversation: Conversation) -> dict:
    _save_cart(conversation, [])
    return {
        "success": True,
        "default_message": "Carrito vaciado. 🗑️ Cuando quieras empezar de nuevo, dime qué quieres pedir.",
    }


def _save_cart(conversation: Conversation, cart: list) -> None:
    ctx = dict(conversation.context or {})
    ctx["cart"] = cart
    conversation.context = ctx
