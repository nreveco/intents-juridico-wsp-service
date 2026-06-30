import enum
import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)


def sa_enum(enum_cls, **kwargs):
    return SAEnum(
        enum_cls,
        name=enum_cls.__name__.lower(),
        native_enum=True,
        validate_strings=True,
        values_callable=lambda enum: [e.value for e in enum],
        **kwargs,
    )
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


# ──────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────

class CaseInsensitiveStrEnum(str, enum.Enum):
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            for member in cls:
                if member.value == normalized or member.name.lower() == normalized:
                    return member
        return super()._missing_(value)


class BusinessType(CaseInsensitiveStrEnum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    SHOP = "shop"
    WORKSHOP = "workshop"
    CLINIC = "clinic"
    CONSTRUCTION = "construction"
    LIQUOR_STORE = "liquor_store"
    LAW_FIRM = "law_firm"
    OTHER = "other"


class ConversationStatus(CaseInsensitiveStrEnum):
    ACTIVE = "active"
    HUMAN_HANDOFF = "human_handoff"
    CLOSED = "closed"


class BookingStatus(CaseInsensitiveStrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class QuoteStatus(CaseInsensitiveStrEnum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class LegalArea(CaseInsensitiveStrEnum):
    PENAL = "penal"
    FAMILIA = "familia"
    CIVIL = "civil"


class CaseUrgency(CaseInsensitiveStrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CaseInquiryStatus(CaseInsensitiveStrEnum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CLOSED = "closed"


# ──────────────────────────────────────────────────────────────
# Business (multi-tenant core)
# ──────────────────────────────────────────────────────────────

class Business(Base):
    __tablename__ = "businesses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    # Meta Cloud API phone number ID (unique per WhatsApp number)
    phone_number_id = Column(String(50), unique=True, nullable=False)
    # Each business can have its own Meta token (or share one)
    whatsapp_token = Column(String(500), nullable=False)
    business_type = Column(sa_enum(BusinessType), default=BusinessType.OTHER)
    welcome_message = Column(Text)
    human_support_phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    settings = relationship("BusinessSettings", back_populates="business", uselist=False, cascade="all, delete-orphan")
    legal_categories = relationship("LegalCategory", back_populates="business", cascade="all, delete-orphan")
    legal_services = relationship("LegalService", back_populates="business", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="business", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="business", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="business", cascade="all, delete-orphan")
    case_inquiries = relationship("CaseInquiry", back_populates="business", cascade="all, delete-orphan")


class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), unique=True, nullable=False)

    address = Column(String(500))
    city = Column(String(100))
    maps_url = Column(String(500))

    # JSON: {"lunes": "09:00-22:00", "martes": "09:00-22:00", ...}
    hours = Column(JSON, default=dict)

    currency = Column(String(10), default="CLP")
    currency_symbol = Column(String(5), default="$")

    business = relationship("Business", back_populates="settings")


# ──────────────────────────────────────────────────────────────
# Legal Catalog (reemplaza Category/Product)
# ──────────────────────────────────────────────────────────────

class LegalCategory(Base):
    __tablename__ = "legal_categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    area = Column(sa_enum(LegalArea), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="legal_categories")
    services = relationship("LegalService", back_populates="category")


class LegalService(Base):
    __tablename__ = "legal_services"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("legal_categories.id"), nullable=True)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    # Precio base orientativo (puede variar según caso)
    base_price = Column(Float, nullable=True)
    # Tiempo estimado (ej: "2-4 semanas", "3-6 meses")
    estimated_timeframe = Column(String(100))
    # Requisitos generales
    requirements = Column(Text)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="legal_services")
    category = relationship("LegalCategory", back_populates="services")


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    
    # Tipo de servicio (ej: "Ley 20.000", "VIF", "Mediación Familiar")
    service_type = Column(String(200), nullable=False)
    # Descripción de los honorarios
    description = Column(Text)
    # Rango de precio mínimo-máximo
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    # Opciones de pago (JSON: ["Transferencia", "Efectivo", "Tarjeta"])
    payment_options = Column(JSON, default=list)
    # Facilidades de pago disponibles
    payment_facilities = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ──────────────────────────────────────────────────────────────
# Conversations & Messages
# ──────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    status = Column(sa_enum(ConversationStatus), default=ConversationStatus.ACTIVE)
    # Keeps last 8 turns {role, content} for context injection
    context = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    business = relationship("Business", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    direction = Column(String(10), nullable=False)  # "inbound" | "outbound"
    content = Column(Text, nullable=False)
    intent = Column(String(50))
    wa_message_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")


# ──────────────────────────────────────────────────────────────
# Case Inquiries (Consultas de Casos - reemplaza Orders)
# ──────────────────────────────────────────────────────────────

class CaseInquiry(Base):
    __tablename__ = "case_inquiries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    
    # Área legal (penal, familia, civil)
    legal_area = Column(sa_enum(LegalArea), nullable=True)
    # Asunto legal específico (ej: "tráfico de drogas", "VIF")
    legal_matter = Column(String(200))
    # Descripción del caso
    description = Column(Text)
    
    # Urgencia del caso
    urgency = Column(sa_enum(CaseUrgency), default=CaseUrgency.MEDIUM)
    # Si está detenido
    is_detained = Column(Boolean, default=False)
    # Si tiene antecedentes previos
    has_prior_record = Column(Boolean, nullable=True)
    # Tipo de beneficio buscado (ej: "libertad condicional")
    benefit_type = Column(String(200), nullable=True)
    
    status = Column(sa_enum(CaseInquiryStatus), default=CaseInquiryStatus.PENDING)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    business = relationship("Business", back_populates="case_inquiries")


# ──────────────────────────────────────────────────────────────
# Bookings
# ──────────────────────────────────────────────────────────────

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    datetime_requested = Column(String(200))  # Natural language e.g. "mañana a las 3pm"
    datetime_confirmed = Column(DateTime(timezone=True), nullable=True)
    service = Column(String(200))
    notes = Column(Text)
    status = Column(sa_enum(BookingStatus), default=BookingStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="bookings")


# ──────────────────────────────────────────────────────────────
# Leads
# ──────────────────────────────────────────────────────────────

class Lead(Base):
    __tablename__ = "leads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    phone = Column(String(50), nullable=False)
    name = Column(String(200))
    first_intent = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="leads")


# ──────────────────────────────────────────────────────────────
# Quotes (cotizaciones) — Day 2
# ──────────────────────────────────────────────────────────────

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    # Descripción libre de lo que cotiza (puede ser servicio, obra, reparación...)
    description = Column(Text, nullable=False)
    notes = Column(Text)
    status = Column(sa_enum(QuoteStatus), default=QuoteStatus.DRAFT)
    total = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="quotes")
    items = relationship("QuoteItem", back_populates="quote", cascade="all, delete-orphan")


class QuoteItem(Base):
    __tablename__ = "quote_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quote_id = Column(String(36), ForeignKey("quotes.id"), nullable=False)
    description = Column(String(300), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)

    quote = relationship("Quote", back_populates="items")
