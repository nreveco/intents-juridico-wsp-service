import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, ConversationStatus

logger = logging.getLogger(__name__)


async def request_human_handoff(
    db: AsyncSession,
    conversation_id: str,
    human_support_phone: str,
) -> dict:
    """
    Cambia el estado de la conversación a HUMAN_HANDOFF.
    A partir de ese momento el webhook no procesa más mensajes automáticamente
    hasta que un humano cierre la conversación desde el panel de admin.
    """
    stmt = (
        update(Conversation)
        .where(Conversation.id == conversation_id)
        .values(status=ConversationStatus.HUMAN_HANDOFF)
    )
    await db.execute(stmt)
    await db.commit()

    logger.info(f"Handoff solicitado para conversación {conversation_id}")

    contact_info = f" Puedes contactarnos al {human_support_phone}." if human_support_phone else ""

    return {
        "success": True,
        "data": {"human_phone": human_support_phone},
        "default_message": (
            f"Entendido, te conecto con uno de nuestros agentes. 👨‍💼\n"
            f"En breve te atenderemos.{contact_info}"
        ),
    }
