import enum
from typing import Optional
from pydantic import BaseModel


class Intent(str, enum.Enum):
    # ══════════════════════════════════════════════════════════
    # INTENCIONES LEGALES - ESTUDIO JURÍDICO
    # ══════════════════════════════════════════════════════════
    
    # Mantener (útiles para contexto legal)
    GREETING = "GREETING"              # Hola / buenos días / quiero información
    THANKS = "THANKS"                  # Gracias / muchas gracias / perfecto gracias
    BOOKING = "BOOKING"                # Quiero agendar consulta / reunión
    QUOTE_REQUEST = "QUOTE_REQUEST"    # Quiero presupuesto / cotización
    HUMAN_SUPPORT = "HUMAN_SUPPORT"    # Hablar con abogado / urgente / estoy detenido
    HOURS_QUERY = "HOURS_QUERY"        # ¿A qué hora atienden?
    LOCATION_QUERY = "LOCATION_QUERY"  # ¿Dónde está la oficina?
    
    # Nuevas intenciones para estudio jurídico
    CASE_INQUIRY = "CASE_INQUIRY"              # ¿Pueden ayudarme? / Tengo un caso de...
    SERVICE_INFO = "SERVICE_INFO"              # ¿Ven temas penales? / ¿Atienden VIF?
    PAYMENT_INFO = "PAYMENT_INFO"              # ¿Cómo son los pagos? / ¿Cuánto cobran?
    TIMEFRAME_QUERY = "TIMEFRAME_QUERY"        # ¿Cuánto demora? / ¿Cuánto tiempo tarda?
    LAWYER_IDENTITY = "LAWYER_IDENTITY"        # ¿Con quién hablo? / ¿Quién eres?
    BENEFIT_INFO = "BENEFIT_INFO"              # ¿Puedo salir en libertad condicional?
    PRIOR_RECORD_QUERY = "PRIOR_RECORD_QUERY"  # ¿Qué pasa con mis antecedentes?
    
    UNKNOWN = "UNKNOWN"                # No se pudo clasificar


class ExtractedIntent(BaseModel):
    """
    Resultado del clasificador IA para estudio jurídico.
    La IA SOLO extrae intención + entidades legales — NO responde al cliente.
    """
    intent: Intent
    
    # ══════════════════════════════════════════════════════════
    # CAMPOS LEGALES
    # ══════════════════════════════════════════════════════════
    
    # Área y asunto legal
    legal_area: Optional[str] = None            # "penal" | "familia" | "civil"
    legal_matter: Optional[str] = None          # "tráfico de drogas", "VIF", "custodia"
    
    # Contexto del caso
    description: Optional[str] = None           # Descripción breve del caso
    is_detained: Optional[bool] = None          # Si está detenido (CRÍTICO ⚠️)
    has_prior_record: Optional[bool] = None     # Si tiene antecedentes previos
    benefit_type: Optional[str] = None          # "libertad condicional", "salida alternativa"
    
    # Urgencia
    urgency: Optional[str] = None               # "low" | "medium" | "high"
    
    # ══════════════════════════════════════════════════════════
    # CAMPOS GENERALES (mantener)
    # ══════════════════════════════════════════════════════════
    
    service: Optional[str] = None               # Servicio legal específico solicitado
    datetime_requested: Optional[str] = None    # Para BOOKING: "mañana 3pm"
    quote_description: Optional[str] = None     # Para QUOTE_REQUEST: descripción

