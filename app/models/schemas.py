from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.db.models import BookingStatus, BusinessType, QuoteStatus


# ──────────────────────────────────────────────────────────────
# Business
# ──────────────────────────────────────────────────────────────

class BusinessCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    phone_number_id: str = Field(..., description="Meta Cloud API phone number ID")
    whatsapp_token: str = Field(..., description="Token permanente o temporal de Meta")
    business_type: BusinessType = BusinessType.OTHER
    welcome_message: Optional[str] = None
    human_support_phone: Optional[str] = None
    # Settings opcionales
    address: Optional[str] = None
    city: Optional[str] = None
    maps_url: Optional[str] = None
    hours: Optional[Dict[str, str]] = Field(
        default=None,
        description='Ej: {"lunes": "09:00-22:00", "martes": "09:00-22:00"}'
    )
    currency_symbol: Optional[str] = "$"


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    welcome_message: Optional[str] = None
    human_support_phone: Optional[str] = None
    is_active: Optional[bool] = None
    address: Optional[str] = None
    city: Optional[str] = None
    maps_url: Optional[str] = None
    hours: Optional[Dict[str, str]] = None


class BusinessResponse(BaseModel):
    id: str
    name: str
    phone_number_id: str
    business_type: BusinessType
    welcome_message: Optional[str]
    human_support_phone: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────────
# Legal Catalog
# ──────────────────────────────────────────────────────────────

class LegalCategoryCreate(BaseModel):
    area: str = Field(..., min_length=2, max_length=50, description="Área legal: penal, familia o civil")
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class LegalCategoryResponse(BaseModel):
    id: str
    area: str
    name: str
    description: Optional[str]
    is_active: bool

    model_config = {"from_attributes": True}


class LegalServiceCreate(BaseModel):
    category_id: Optional[str] = None
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = None
    estimated_timeframe: Optional[str] = None
    requirements: Optional[str] = None
    is_available: bool = True


class LegalServiceResponse(BaseModel):
    id: str
    business_id: str
    category_id: Optional[str]
    name: str
    description: Optional[str]
    base_price: Optional[float]
    estimated_timeframe: Optional[str]
    requirements: Optional[str]
    is_available: bool

    model_config = {"from_attributes": True}


class CaseInquiryStatusUpdate(BaseModel):
    status: str


class CaseInquiryResponse(BaseModel):
    id: str
    customer_phone: str
    customer_name: Optional[str]
    legal_area: Optional[str]
    legal_matter: Optional[str]
    description: Optional[str]
    urgency: Optional[str]
    is_detained: bool
    has_prior_record: Optional[bool]
    benefit_type: Optional[str]
    status: str
    created_at: str
    updated_at: Optional[str]

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────────
# Booking
# ──────────────────────────────────────────────────────────────

class BookingStatusUpdate(BaseModel):
    status: BookingStatus


class BookingResponse(BaseModel):
    id: str
    customer_phone: str
    customer_name: Optional[str]
    service: Optional[str]
    datetime_requested: Optional[str]
    status: BookingStatus

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────

class DashboardResponse(BaseModel):
    total_conversations: int
    total_leads: int
    total_orders: int
    total_revenue: float
    pending_orders: int
    pending_bookings: int


# ──────────────────────────────────────────────────────────────
# Quote
# ──────────────────────────────────────────────────────────────

class QuoteStatusUpdate(BaseModel):
    status: QuoteStatus


class QuoteItemCreate(BaseModel):
    description: str = Field(..., min_length=2, max_length=300)
    quantity: int = Field(1, ge=1)
    unit_price: float = Field(..., gt=0)


class QuoteItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class QuoteResponse(BaseModel):
    id: str
    customer_phone: str
    customer_name: Optional[str]
    description: Optional[str]
    status: QuoteStatus
    total: float
    items: List[QuoteItemResponse] = []

    model_config = {"from_attributes": True}
