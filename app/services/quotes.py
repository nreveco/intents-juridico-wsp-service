import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Quote, QuoteItem, QuoteStatus

logger = logging.getLogger(__name__)


async def create_quote_request(
    db: AsyncSession,
    business_id: str,
    customer_phone: str,
    description: str,
    customer_name: str = "",
) -> dict:
    """
    Registra una solicitud de cotización pendiente.
    El dueño del negocio la completa con precios desde el panel admin.
    """
    quote_id = str(uuid.uuid4())

    quote = Quote(
        id=quote_id,
        business_id=business_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        description=description,
        status=QuoteStatus.DRAFT,
        total=0.0,
    )

    db.add(quote)
    await db.commit()

    short_id = quote_id[:8].upper()
    logger.info(f"Cotización creada: {short_id} — {description[:60]}")

    return {
        "success": True,
        "data": {
            "quote_id": short_id,
            "description": description,
            "status": "borrador — pendiente de valorización",
        },
        "default_message": (
            f"✅ Solicitud de cotización registrada!\n"
            f"• Descripción: {description}\n"
            f"• ID: #{short_id}\n\n"
            f"Te enviaremos el presupuesto a la brevedad. 📋"
        ),
    }
