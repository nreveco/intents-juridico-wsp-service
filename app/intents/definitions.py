import enum
from typing import Optional
from pydantic import BaseModel


class Intent(str, enum.Enum):
    PRICE_QUERY = "PRICE_QUERY"        # ¿Cuánto cuesta X?
    PRODUCT_INFO = "PRODUCT_INFO"      # ¿Qué tiene X? ¿tienen X?
    ORDER_CREATE = "ORDER_CREATE"      # Quiero pedir / dame X
    ORDER_STATUS = "ORDER_STATUS"      # ¿Cómo va mi pedido?
    BOOKING = "BOOKING"                # Quiero reservar / agendar
    QUOTE_REQUEST = "QUOTE_REQUEST"    # Quiero cotización / presupuesto
    HUMAN_SUPPORT = "HUMAN_SUPPORT"    # Hablar con persona / queja / urgente
    GREETING = "GREETING"              # Hola / buenos días
    HOURS_QUERY = "HOURS_QUERY"        # ¿A qué hora abren?
    LOCATION_QUERY = "LOCATION_QUERY"  # ¿Dónde están? / dirección
    # Day 2 — carrito multi-ítem
    CART_ADD = "CART_ADD"              # "Agrega X al pedido"
    CART_VIEW = "CART_VIEW"            # "Ver mi carrito / qué tengo"
    CART_CHECKOUT = "CART_CHECKOUT"    # "Confirmar pedido / listo / pagar"
    CART_CLEAR = "CART_CLEAR"          # "Vaciar carrito / cancelar"
    UNKNOWN = "UNKNOWN"                # No se pudo clasificar


class ExtractedIntent(BaseModel):
    """
    Resultado del clasificador IA.
    La IA SOLO extrae intención + entidades — NO responde al cliente.
    """
    intent: Intent
    product_name: Optional[str] = None       # Nombre del producto mencionado
    quantity: Optional[int] = None           # Cantidad pedida
    service: Optional[str] = None           # Servicio para reserva o cotización
    datetime_requested: Optional[str] = None # Fecha/hora en lenguaje natural
    order_id: Optional[str] = None          # ID de pedido mencionado
    quote_description: Optional[str] = None # Descripción libre para cotización
    urgency: Optional[str] = None           # "low" | "medium" | "high"
