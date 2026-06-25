"""
Servicio para gestión de servicios legales.
Reemplaza products.py en el contexto de estudio jurídico.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import LegalService, LegalCategory, LegalArea


async def search_legal_services(
    db: AsyncSession,
    business_id: str,
    legal_area: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: int = 10
) -> List[dict]:
    """
    Busca servicios legales por área legal o texto de búsqueda.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del negocio (estudio jurídico)
        legal_area: "penal" | "familia" | "civil" (opcional)
        search_query: Texto de búsqueda en nombre/descripción (opcional)
        limit: Máximo de resultados
    
    Returns:
        Lista de servicios legales con información de categoría
    """
    query = select(LegalService).where(
        LegalService.business_id == business_id,
        LegalService.is_available == True
    )
    
    # Filtrar por área legal si se especifica
    if legal_area:
        # Normalizar área legal
        area_map = {
            "penal": LegalArea.PENAL,
            "familia": LegalArea.FAMILIA,
            "civil": LegalArea.CIVIL
        }
        area_enum = area_map.get(legal_area.lower())
        if area_enum:
            # Join con categoría para filtrar por área
            query = query.join(LegalCategory).where(
                LegalCategory.area == area_enum
            )
    
    # Filtrar por búsqueda de texto
    if search_query:
        search_term = f"%{search_query.lower()}%"
        query = query.where(
            (LegalService.name.ilike(search_term)) |
            (LegalService.description.ilike(search_term))
        )
    
    query = query.limit(limit)
    result = await db.execute(query)
    services = result.scalars().all()
    
    # Convertir a diccionarios con información enriquecida
    services_list = []
    for service in services:
        # Cargar categoría si existe
        category_info = None
        if service.category_id:
            cat_query = select(LegalCategory).where(
                LegalCategory.id == service.category_id
            )
            cat_result = await db.execute(cat_query)
            category = cat_result.scalar_one_or_none()
            if category:
                category_info = {
                    "name": category.name,
                    "area": category.area.value
                }
        
        services_list.append({
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "base_price": service.base_price,
            "estimated_timeframe": service.estimated_timeframe,
            "requirements": service.requirements,
            "category": category_info
        })
    
    return services_list


async def get_service_by_id(
    db: AsyncSession,
    business_id: str,
    service_id: str
) -> Optional[dict]:
    """
    Obtiene un servicio legal específico por ID.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del negocio
        service_id: ID del servicio legal
    
    Returns:
        Diccionario con información completa del servicio o None
    """
    query = select(LegalService).where(
        LegalService.id == service_id,
        LegalService.business_id == business_id
    )
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    
    if not service:
        return None
    
    # Cargar información de categoría
    category_info = None
    if service.category_id:
        cat_query = select(LegalCategory).where(
            LegalCategory.id == service.category_id
        )
        cat_result = await db.execute(cat_query)
        category = cat_result.scalar_one_or_none()
        if category:
            category_info = {
                "id": category.id,
                "name": category.name,
                "area": category.area.value,
                "description": category.description
            }
    
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "base_price": service.base_price,
        "estimated_timeframe": service.estimated_timeframe,
        "requirements": service.requirements,
        "is_available": service.is_available,
        "category": category_info,
        "created_at": service.created_at.isoformat() if service.created_at else None
    }


async def get_services_by_legal_matter(
    db: AsyncSession,
    business_id: str,
    legal_matter: str,
    limit: int = 5
) -> List[dict]:
    """
    Busca servicios legales relevantes para un asunto legal específico.
    
    Ejemplo: legal_matter="tráfico de drogas" → servicios relacionados con Ley 20.000
    
    Args:
        db: Sesión de base de datos
        business_id: ID del negocio
        legal_matter: Asunto legal (ej: "tráfico de drogas", "VIF", "custodia")
        limit: Máximo de resultados
    
    Returns:
        Lista de servicios legales relevantes
    """
    # Mapeo de asuntos legales a términos de búsqueda
    matter_keywords = {
        "tráfico de drogas": ["Ley 20.000", "drogas", "tráfico"],
        "vif": ["VIF", "violencia intrafamiliar", "violencia"],
        "custodia": ["custodia", "tuición", "cuidado personal"],
        "pensión alimenticia": ["pensión", "alimenticia", "alimentos"],
        "homicidio": ["homicidio", "delitos contra personas"],
        "beneficios penitenciarios": ["beneficio", "libertad condicional", "salida alternativa"],
        "divorcio": ["divorcio", "separación"],
        "contratos": ["contrato", "compraventa", "arrendamiento"]
    }
    
    # Buscar keywords relevantes
    keywords = matter_keywords.get(legal_matter.lower(), [legal_matter])
    
    # Buscar servicios que coincidan con alguna keyword
    query = select(LegalService).where(
        LegalService.business_id == business_id,
        LegalService.is_available == True
    )
    
    # Construir condición OR para todas las keywords
    conditions = []
    for keyword in keywords:
        search_term = f"%{keyword}%"
        conditions.append(LegalService.name.ilike(search_term))
        conditions.append(LegalService.description.ilike(search_term))
    
    if conditions:
        from sqlalchemy import or_
        query = query.where(or_(*conditions))
    
    query = query.limit(limit)
    result = await db.execute(query)
    services = result.scalars().all()
    
    # Convertir a diccionarios
    services_list = []
    for service in services:
        services_list.append({
            "id": service.id,
            "name": service.name,
            "description": service.description,
            "base_price": service.base_price,
            "estimated_timeframe": service.estimated_timeframe
        })
    
    return services_list


async def get_all_legal_categories(
    db: AsyncSession,
    business_id: str
) -> List[dict]:
    """
    Obtiene todas las categorías legales del estudio.
    
    Args:
        db: Sesión de base de datos
        business_id: ID del negocio
    
    Returns:
        Lista de categorías legales con conteo de servicios
    """
    query = select(LegalCategory).where(
        LegalCategory.business_id == business_id,
        LegalCategory.is_active == True
    )
    result = await db.execute(query)
    categories = result.scalars().all()
    
    categories_list = []
    for category in categories:
        # Contar servicios activos en esta categoría
        services_query = select(LegalService).where(
            LegalService.category_id == category.id,
            LegalService.is_available == True
        )
        services_result = await db.execute(services_query)
        services_count = len(services_result.scalars().all())
        
        categories_list.append({
            "id": category.id,
            "name": category.name,
            "area": category.area.value,
            "description": category.description,
            "services_count": services_count
        })
    
    return categories_list
