"""
Servicio para gestión de información de honorarios legales.
Proporciona información sobre costos y formas de pago.
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FeeStructure, LegalService, BusinessSettings


async def get_fee_structure_by_service_type(
    db: AsyncSession,
    business_id: str,
    service_type: str
) -> Optional[dict]:
    """
    Obtiene la estructura de honorarios para un tipo de servicio específico.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
        service_type: Tipo de servicio (ej: "Ley 20.000", "VIF", "Mediación Familiar")
    
    Returns:
        Diccionario con estructura de honorarios o None
    """
    query = select(FeeStructure).where(
        FeeStructure.business_id == business_id,
        FeeStructure.service_type.ilike(f"%{service_type}%")
    )
    result = await db.execute(query)
    fee_structure = result.scalar_one_or_none()
    
    if not fee_structure:
        return None
    
    return {
        "service_type": fee_structure.service_type,
        "description": fee_structure.description,
        "min_price": fee_structure.min_price,
        "max_price": fee_structure.max_price,
        "payment_options": fee_structure.payment_options,
        "payment_facilities": fee_structure.payment_facilities
    }


async def get_all_fee_structures(
    db: AsyncSession,
    business_id: str
) -> List[dict]:
    """
    Obtiene todas las estructuras de honorarios del estudio.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
    
    Returns:
        Lista de estructuras de honorarios
    """
    query = select(FeeStructure).where(
        FeeStructure.business_id == business_id
    )
    result = await db.execute(query)
    fee_structures = result.scalars().all()
    
    structures_list = []
    for structure in fee_structures:
        structures_list.append({
            "id": structure.id,
            "service_type": structure.service_type,
            "description": structure.description,
            "min_price": structure.min_price,
            "max_price": structure.max_price,
            "payment_options": structure.payment_options,
            "payment_facilities": structure.payment_facilities
        })
    
    return structures_list


async def get_payment_options(
    db: AsyncSession,
    business_id: str
) -> dict:
    """
    Obtiene las formas de pago disponibles y facilidades generales del estudio.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
    
    Returns:
        Diccionario con opciones de pago generales
    """
    # Obtener configuración del negocio
    settings_query = select(BusinessSettings).where(
        BusinessSettings.business_id == business_id
    )
    settings_result = await db.execute(settings_query)
    settings = settings_result.scalar_one_or_none()
    
    # Información por defecto
    currency = settings.currency if settings else "CLP"
    currency_symbol = settings.currency_symbol if settings else "$"
    
    # Obtener todas las opciones de pago únicas de todas las estructuras
    fee_query = select(FeeStructure).where(
        FeeStructure.business_id == business_id
    )
    fee_result = await db.execute(fee_query)
    fee_structures = fee_result.scalars().all()
    
    # Consolidar opciones de pago
    all_payment_options = set()
    all_facilities = []
    
    for structure in fee_structures:
        if structure.payment_options:
            all_payment_options.update(structure.payment_options)
        if structure.payment_facilities:
            all_facilities.append(structure.payment_facilities)
    
    return {
        "currency": currency,
        "currency_symbol": currency_symbol,
        "payment_methods": list(all_payment_options) if all_payment_options else [
            "Transferencia bancaria",
            "Efectivo",
            "Tarjeta de crédito/débito"
        ],
        "facilities": all_facilities if all_facilities else [
            "Consulta inicial gratuita",
            "Planes de pago personalizados según el caso"
        ]
    }


async def get_estimated_fee_for_legal_matter(
    db: AsyncSession,
    business_id: str,
    legal_matter: str
) -> Optional[dict]:
    """
    Obtiene una estimación de honorarios para un asunto legal específico.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
        legal_matter: Asunto legal (ej: "tráfico de drogas", "VIF", "custodia")
    
    Returns:
        Diccionario con estimación de honorarios o None
    """
    # Mapeo de asuntos legales a tipos de servicio
    matter_to_service = {
        "tráfico de drogas": "Ley 20.000",
        "drogas": "Ley 20.000",
        "vif": "VIF",
        "violencia intrafamiliar": "VIF",
        "custodia": "Tuición y Custodia",
        "tuición": "Tuición y Custodia",
        "pensión alimenticia": "Pensión Alimenticia",
        "alimentos": "Pensión Alimenticia",
        "divorcio": "Divorcio",
        "homicidio": "Delitos contra Personas",
        "contratos": "Contratos"
    }
    
    service_type = matter_to_service.get(legal_matter.lower(), legal_matter)
    
    # Buscar fee structure
    fee_structure = await get_fee_structure_by_service_type(db, business_id, service_type)
    
    if fee_structure:
        return fee_structure
    
    # Si no hay fee structure específica, buscar en servicios legales
    service_query = select(LegalService).where(
        LegalService.business_id == business_id,
        LegalService.name.ilike(f"%{service_type}%")
    )
    service_result = await db.execute(service_query)
    legal_service = service_result.scalar_one_or_none()
    
    if legal_service and legal_service.base_price:
        return {
            "service_type": legal_service.name,
            "description": legal_service.description,
            "min_price": legal_service.base_price,
            "max_price": None,
            "estimated_timeframe": legal_service.estimated_timeframe,
            "payment_options": ["Transferencia", "Efectivo", "Tarjeta"],
            "payment_facilities": "Consulta inicial gratuita. Planes de pago disponibles."
        }
    
    return None


async def format_fee_info_for_response(
    db: AsyncSession,
    business_id: str,
    legal_matter: Optional[str] = None
) -> str:
    """
    Formatea información de honorarios para respuesta de WhatsApp.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del estudio jurídico
        legal_matter: Asunto legal específico (opcional)
    
    Returns:
        Texto formateado para respuesta de WhatsApp
    """
    # Obtener opciones de pago generales
    payment_info = await get_payment_options(db, business_id)
    currency_symbol = payment_info["currency_symbol"]
    
    # Si hay un asunto legal específico, buscar honorarios
    if legal_matter:
        fee_estimate = await get_estimated_fee_for_legal_matter(db, business_id, legal_matter)
        
        if fee_estimate:
            response = f"📋 **Honorarios para {fee_estimate['service_type']}**\n\n"
            
            if fee_estimate.get("min_price") and fee_estimate.get("max_price"):
                response += f"Rango: {currency_symbol}{fee_estimate['min_price']:,.0f} - {currency_symbol}{fee_estimate['max_price']:,.0f}\n"
            elif fee_estimate.get("min_price"):
                response += f"Desde: {currency_symbol}{fee_estimate['min_price']:,.0f}\n"
            
            if fee_estimate.get("description"):
                response += f"\n{fee_estimate['description']}\n"
            
            response += f"\n💳 Formas de pago: {', '.join(payment_info['payment_methods'])}\n"
            
            if fee_estimate.get("payment_facilities"):
                response += f"\n✅ {fee_estimate['payment_facilities']}"
            
            response += "\n\n⚖️ El costo exacto depende de la complejidad de cada caso."
            return response
    
    # Información general de honorarios
    response = "📋 **Información de Honorarios**\n\n"
    response += "Nuestros honorarios varían según la complejidad del caso y el área legal.\n\n"
    response += f"💳 Formas de pago: {', '.join(payment_info['payment_methods'])}\n\n"
    
    if payment_info.get("facilities"):
        response += "✅ Facilidades:\n"
        for facility in payment_info["facilities"]:
            response += f"• {facility}\n"
    
    response += "\n⚖️ Para un presupuesto personalizado, agenda una consulta gratuita."
    
    return response
