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
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


# ──────────────────────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────────────────────

class BusinessType(str, enum.Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    SHOP = "shop"
    WORKSHOP = "workshop"
    CLINIC = "clinic"
    CONSTRUCTION = "construction"
    LIQUOR_STORE = "liquor_store"
    OTHER = "other"


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    HUMAN_HANDOFF = "human_handoff"
    CLOSED = "closed"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class QuoteStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


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
    business_type = Column(SAEnum(BusinessType), default=BusinessType.OTHER)
    welcome_message = Column(Text)
    human_support_phone = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    settings = relationship("BusinessSettings", back_populates="business", uselist=False, cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="business", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="business", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="business", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="business", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="business", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="business", cascade="all, delete-orphan")


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
# Catalog
# ──────────────────────────────────────────────────────────────

class Category(Base):
    __tablename__ = "categories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    business = relationship("Business", back_populates="categories")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="products")
    category = relationship("Category", back_populates="products")


# ──────────────────────────────────────────────────────────────
# Conversations & Messages
# ──────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    status = Column(SAEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
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
# Orders
# ──────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    business_id = Column(String(36), ForeignKey("businesses.id"), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    customer_name = Column(String(200))
    status = Column(SAEnum(OrderStatus), default=OrderStatus.PENDING)
    total = Column(Float, default=0.0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    business = relationship("Business", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


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
    status = Column(SAEnum(BookingStatus), default=BookingStatus.PENDING)
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
    status = Column(SAEnum(QuoteStatus), default=QuoteStatus.DRAFT)
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
