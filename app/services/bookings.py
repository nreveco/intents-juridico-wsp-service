import uuid
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Booking, BookingStatus

logger = logging.getLogger(__name__)


async def create_booking(
    db: AsyncSession,
    business_id: str,
    customer_phone: str,
    service: str,
    datetime_requested: str,
    customer_name: str = "",
    notes: str = "",
) -> dict:
    """Registra una solicitud de reserva. El negocio confirma manualmente desde el panel."""
    booking_id = str(uuid.uuid4())

    booking = Booking(
        id=booking_id,
        business_id=business_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        service=service or "consulta general",
        datetime_requested=datetime_requested,
        notes=notes,
        status=BookingStatus.PENDING,
    )

    db.add(booking)
    await db.commit()

    short_id = booking_id[:8].upper()
    logger.info(f"Reserva creada: {short_id} — {service} para {datetime_requested}")

    return {
        "success": True,
        "data": {
            "booking_id": short_id,
            "service": service,
            "datetime_requested": datetime_requested,
            "status": "pendiente de confirmación",
        },
        "default_message": (
            f"✅ Reserva registrada!\n"
            f"• Servicio: {service}\n"
            f"• Fecha/hora: {datetime_requested}\n"
            f"• ID: #{short_id}\n\n"
            "Te contactaremos para confirmar. 📅"
        ),
    }
