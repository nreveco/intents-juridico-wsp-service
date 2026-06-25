"""
Servicio para gestión de consultas de casos legales.
Reemplaza orders.py en el contexto de estudio jurídico.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CaseInquiry, 
    LegalArea, 
    CaseUrgency, 
    CaseInquiryStatus,
    Business
)


async def create_case_inquiry(
    db: AsyncSession,
    business_id: str,
    customer_phone: str,
    customer_name: Optional[str] = None,
    legal_area: Optional[str] = None,
    legal_matter: Optional[str] = None,
    description: Optional[str] = None,
    urgency: str = "medium",
    is_detained: bool = False,
    has_prior_record: Optional[bool] = None,
    benefit_type: Optional[str] = None,
    notes: Optional[str] = None
) -> dict:
    """
    Crea una nueva consulta de caso legal.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
        customer_phone: Teléfono del cliente
        customer_name: Nombre del cliente (opcional)
        legal_area: "penal" | "familia" | "civil"
        legal_matter: Asunto específico (ej: "tráfico de drogas", "VIF")
        description: Descripción del caso
        urgency: "low" | "medium" | "high"
        is_detained: Si está detenido (CRÍTICO)
        has_prior_record: Si tiene antecedentes previos
        benefit_type: Tipo de beneficio solicitado
        notes: Notas adicionales
    
    Returns:
        Diccionario con la consulta creada
    """
    # Normalizar área legal a enum
    area_enum = None
    if legal_area:
        area_map = {
            "penal": LegalArea.PENAL,
            "familia": LegalArea.FAMILIA,
            "civil": LegalArea.CIVIL
        }
        area_enum = area_map.get(legal_area.lower())
    
    # Normalizar urgencia a enum
    urgency_map = {
        "low": CaseUrgency.LOW,
        "medium": CaseUrgency.MEDIUM,
        "high": CaseUrgency.HIGH
    }
    urgency_enum = urgency_map.get(urgency.lower(), CaseUrgency.MEDIUM)
    
    # Si está detenido, SIEMPRE es urgencia alta
    if is_detained:
        urgency_enum = CaseUrgency.HIGH
    
    # Crear consulta
    inquiry = CaseInquiry(
        business_id=business_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        legal_area=area_enum,
        legal_matter=legal_matter,
        description=description,
        urgency=urgency_enum,
        is_detained=is_detained,
        has_prior_record=has_prior_record,
        benefit_type=benefit_type,
        status=CaseInquiryStatus.PENDING,
        notes=notes
    )
    
    db.add(inquiry)
    await db.commit()
    await db.refresh(inquiry)
    
    # Si es urgente o está detenido, notificar (se implementa en notificaciones)
    if urgency_enum == CaseUrgency.HIGH or is_detained:
        # TODO: Llamar a servicio de notificaciones urgentes
        pass
    
    return {
        "id": inquiry.id,
        "customer_phone": inquiry.customer_phone,
        "customer_name": inquiry.customer_name,
        "legal_area": inquiry.legal_area.value if inquiry.legal_area else None,
        "legal_matter": inquiry.legal_matter,
        "description": inquiry.description,
        "urgency": inquiry.urgency.value,
        "is_detained": inquiry.is_detained,
        "has_prior_record": inquiry.has_prior_record,
        "benefit_type": inquiry.benefit_type,
        "status": inquiry.status.value,
        "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None
    }


async def get_case_inquiry(
    db: AsyncSession,
    inquiry_id: str,
    business_id: str
) -> Optional[dict]:
    """
    Obtiene una consulta de caso por ID.
    
    Args:
        db: Sesión de base de datos
        inquiry_id: ID de la consulta
        business_id: ID del negocio
    
    Returns:
        Diccionario con la consulta o None
    """
    query = select(CaseInquiry).where(
        CaseInquiry.id == inquiry_id,
        CaseInquiry.business_id == business_id
    )
    result = await db.execute(query)
    inquiry = result.scalar_one_or_none()
    
    if not inquiry:
        return None
    
    return {
        "id": inquiry.id,
        "customer_phone": inquiry.customer_phone,
        "customer_name": inquiry.customer_name,
        "legal_area": inquiry.legal_area.value if inquiry.legal_area else None,
        "legal_matter": inquiry.legal_matter,
        "description": inquiry.description,
        "urgency": inquiry.urgency.value,
        "is_detained": inquiry.is_detained,
        "has_prior_record": inquiry.has_prior_record,
        "benefit_type": inquiry.benefit_type,
        "status": inquiry.status.value,
        "notes": inquiry.notes,
        "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None,
        "updated_at": inquiry.updated_at.isoformat() if inquiry.updated_at else None
    }


async def update_case_inquiry_status(
    db: AsyncSession,
    inquiry_id: str,
    business_id: str,
    new_status: str,
    notes: Optional[str] = None
) -> Optional[dict]:
    """
    Actualiza el estado de una consulta de caso.
    
    Args:
        db: Sesión de base de datos
        inquiry_id: ID de la consulta
        business_id: ID del negocio
        new_status: "pending" | "in_review" | "accepted" | "rejected" | "closed"
        notes: Notas adicionales (opcional)
    
    Returns:
        Diccionario con la consulta actualizada o None
    """
    query = select(CaseInquiry).where(
        CaseInquiry.id == inquiry_id,
        CaseInquiry.business_id == business_id
    )
    result = await db.execute(query)
    inquiry = result.scalar_one_or_none()
    
    if not inquiry:
        return None
    
    # Normalizar estado a enum
    status_map = {
        "pending": CaseInquiryStatus.PENDING,
        "in_review": CaseInquiryStatus.IN_REVIEW,
        "accepted": CaseInquiryStatus.ACCEPTED,
        "rejected": CaseInquiryStatus.REJECTED,
        "closed": CaseInquiryStatus.CLOSED
    }
    status_enum = status_map.get(new_status.lower())
    
    if not status_enum:
        return None
    
    inquiry.status = status_enum
    if notes:
        inquiry.notes = notes if not inquiry.notes else f"{inquiry.notes}\n{notes}"
    
    await db.commit()
    await db.refresh(inquiry)
    
    return {
        "id": inquiry.id,
        "status": inquiry.status.value,
        "notes": inquiry.notes,
        "updated_at": inquiry.updated_at.isoformat() if inquiry.updated_at else None
    }


async def get_pending_urgent_inquiries(
    db: AsyncSession,
    business_id: str,
    limit: int = 20
) -> list:
    """
    Obtiene todas las consultas pendientes con urgencia alta.
    Útil para dashboard del abogado.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del negocio
        limit: Máximo de resultados
    
    Returns:
        Lista de consultas urgentes pendientes
    """
    query = select(CaseInquiry).where(
        CaseInquiry.business_id == business_id,
        CaseInquiry.status == CaseInquiryStatus.PENDING,
        CaseInquiry.urgency == CaseUrgency.HIGH
    ).order_by(CaseInquiry.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    inquiries = result.scalars().all()
    
    inquiries_list = []
    for inquiry in inquiries:
        inquiries_list.append({
            "id": inquiry.id,
            "customer_phone": inquiry.customer_phone,
            "customer_name": inquiry.customer_name,
            "legal_matter": inquiry.legal_matter,
            "is_detained": inquiry.is_detained,
            "created_at": inquiry.created_at.isoformat() if inquiry.created_at else None
        })
    
    return inquiries_list


async def notify_urgent_case(
    db: AsyncSession,
    inquiry_id: str,
    business_id: str
) -> bool:
    """
    Notifica al abogado sobre un caso urgente.
    
    Args:
        db: Sesión de base de datos
        inquiry_id: ID de la consulta urgente
        business_id: ID del negocio
    
    Returns:
        True si se notificó exitosamente
    """
    # Obtener información del caso
    inquiry = await get_case_inquiry(db, inquiry_id, business_id)
    if not inquiry:
        return False
    
    # Obtener información del negocio para número de soporte
    business_query = select(Business).where(Business.id == business_id)
    business_result = await db.execute(business_query)
    business = business_result.scalar_one_or_none()
    
    if not business or not business.human_support_phone:
        return False
    
    # TODO: Integrar con servicio de notificaciones (WhatsApp, SMS, Email)
    # Por ahora, solo registramos el intento
    print(f"⚠️ CASO URGENTE - Notificar a {business.human_support_phone}")
    print(f"   Cliente: {inquiry['customer_phone']}")
    print(f"   Asunto: {inquiry['legal_matter']}")
    print(f"   Detenido: {inquiry['is_detained']}")
    
    return True
