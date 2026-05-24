import uuid
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, OrderItem, OrderStatus, Product

logger = logging.getLogger(__name__)

ORDER_STATUS_ES = {
    "pending": "pendiente ⏳",
    "confirmed": "confirmado ✅",
    "preparing": "en preparación 👨‍🍳",
    "ready": "listo para retirar 🎉",
    "delivered": "entregado ✅",
    "cancelled": "cancelado ❌",
}


async def create_order(
    db: AsyncSession,
    business_id: str,
    customer_phone: str,
    product_query: str,
    quantity: int = 1,
    customer_name: str = "",
) -> dict:
    """Crea un pedido buscando el producto en la DB real."""
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
            "data": None,
            "default_message": (
                f"No encontré '{product_query}' en nuestro catálogo. 😕\n"
                "Te paso con nuestro equipo para ayudarte con el pedido."
            ),
        }

    order_id = str(uuid.uuid4())
    order = Order(
        id=order_id,
        business_id=business_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        status=OrderStatus.PENDING,
        total=round(product.price * quantity, 2),
    )

    item = OrderItem(
        id=str(uuid.uuid4()),
        order_id=order_id,
        product_id=product.id,
        product_name=product.name,
        quantity=quantity,
        unit_price=product.price,
    )

    db.add(order)
    db.add(item)
    await db.commit()

    short_id = order_id[:8].upper()
    logger.info(f"Pedido creado: {short_id} — {product.name} x{quantity} = ${order.total}")

    return {
        "success": True,
        "data": {
            "order_id": short_id,
            "product": product.name,
            "quantity": quantity,
            "unit_price": product.price,
            "total": order.total,
            "status": ORDER_STATUS_ES["pending"],
        },
    }


async def get_order_status(
    db: AsyncSession, business_id: str, customer_phone: str
) -> dict:
    """Devuelve el último pedido del cliente."""
    stmt = (
        select(Order)
        .where(
            Order.business_id == business_id,
            Order.customer_phone == customer_phone,
        )
        .order_by(Order.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        return {
            "found": False,
            "data": None,
            "default_message": "No encontré pedidos recientes a tu nombre. 🤔",
        }

    return {
        "found": True,
        "data": {
            "order_id": order.id[:8].upper(),
            "status": ORDER_STATUS_ES.get(order.status.value, order.status.value),
            "total": order.total,
        },
    }
