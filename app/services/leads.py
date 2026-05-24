import uuid
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Lead

logger = logging.getLogger(__name__)


async def register_lead(
    db: AsyncSession,
    business_id: str,
    phone: str,
    name: str | None = None,
    intent: str | None = None,
) -> None:
    """Registra un lead la primera vez que un cliente escribe. Idempotente."""
    stmt = select(Lead).where(
        Lead.business_id == business_id,
        Lead.phone == phone,
    ).limit(1)

    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if not existing:
        lead = Lead(
            id=str(uuid.uuid4()),
            business_id=business_id,
            phone=phone,
            name=name,
            first_intent=intent,
        )
        db.add(lead)
        await db.commit()
        logger.info(f"Nuevo lead registrado: {phone} | intent={intent}")
