import logging
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category, Product

logger = logging.getLogger(__name__)


async def find_product_by_name(
    db: AsyncSession, business_id: str, product_name: str
) -> dict:
    """
    Busca un producto por nombre usando ILIKE sobre cada palabra.
    Devuelve precio y descripción real — nunca inventa.
    """
    words = [w for w in product_name.lower().split() if len(w) > 2]
    if not words:
        words = [product_name.lower()]

    conditions = [Product.name.ilike(f"%{w}%") for w in words]

    stmt = (
        select(Product)
        .where(
            Product.business_id == business_id,
            Product.is_available == True,
            or_(*conditions),
        )
        .limit(6)
    )

    result = await db.execute(stmt)
    products = result.scalars().all()

    if not products:
        return {
            "found": False,
            "data": None,
            "default_message": (
                f"No encontré '{product_name}' en nuestro catálogo. 🤔\n"
                "¿Podrías escribirlo de otra manera o preguntar por el menú completo?"
            ),
        }

    if len(products) == 1:
        p = products[0]
        return {
            "found": True,
            "multiple": False,
            "data": {"name": p.name, "price": p.price, "description": p.description},
        }

    return {
        "found": True,
        "multiple": True,
        "data": [
            {"name": p.name, "price": p.price, "description": p.description}
            for p in products
        ],
    }


async def get_menu_by_category(
    db: AsyncSession,
    business_id: str,
    category_name: Optional[str] = None,
) -> dict:
    """Devuelve el menú/catálogo agrupado por categoría."""
    stmt = select(Product, Category).join(
        Category, Product.category_id == Category.id, isouter=True
    ).where(
        Product.business_id == business_id,
        Product.is_available == True,
    )

    if category_name:
        stmt = stmt.where(Category.name.ilike(f"%{category_name}%"))

    result = await db.execute(stmt)
    rows = result.all()

    if not rows:
        return {
            "found": False,
            "data": None,
            "default_message": "Por el momento no tenemos productos cargados. Te comunico con nuestro equipo. 😊",
        }

    grouped: dict = {}
    for product, category in rows:
        cat_name = category.name if category else "Otros"
        grouped.setdefault(cat_name, [])
        grouped[cat_name].append({"name": product.name, "price": product.price})

    return {"found": True, "data": grouped}
