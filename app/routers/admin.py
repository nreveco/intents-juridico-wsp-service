import uuid
import logging

from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import get_db
from app.db.models import (
    Booking,
    BookingStatus,
    Business,
    BusinessSettings,
    LegalCategory,
    LegalService,
    Conversation,
    ConversationStatus,
    Lead,
    Message,
    Quote,
    QuoteItem,
    QuoteStatus,
)
from app.models.schemas import (
    BookingResponse,
    BookingStatusUpdate,
    BusinessCreate,
    BusinessResponse,
    BusinessUpdate,
    DashboardResponse,
    LegalCategoryCreate,
    LegalCategoryResponse,
    LegalServiceCreate,
    LegalServiceResponse,
    QuoteItemCreate,
    QuoteItemResponse,
    QuoteResponse,
    QuoteStatusUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# ── API Key simple para proteger el panel ─────────────────────
api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=True)


def require_admin_key(key: str = Security(api_key_header)) -> str:
    if key != settings.admin_api_key:
        raise HTTPException(status_code=403, detail="Invalid admin API key")
    return key


# ──────────────────────────────────────────────────────────────
# Businesses
# ──────────────────────────────────────────────────────────────

@router.post("/businesses", response_model=BusinessResponse, status_code=201)
async def create_business(
    data: BusinessCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    # Verificar duplicados
    dup = await db.execute(
        select(Business).where(Business.phone_number_id == data.phone_number_id)
    )
    if dup.scalar_one_or_none():
        raise HTTPException(400, "phone_number_id ya registrado")

    business_id = str(uuid.uuid4())
    business = Business(
        id=business_id,
        name=data.name,
        phone_number_id=data.phone_number_id,
        whatsapp_token=data.whatsapp_token,
        business_type=data.business_type,
        welcome_message=data.welcome_message,
        human_support_phone=data.human_support_phone,
    )
    db.add(business)

    biz_settings = BusinessSettings(
        id=str(uuid.uuid4()),
        business_id=business_id,
        address=data.address,
        city=data.city,
        maps_url=data.maps_url,
        hours=data.hours or {},
        currency_symbol=data.currency_symbol or "$",
    )
    db.add(biz_settings)

    await db.commit()
    await db.refresh(business)
    return business


@router.get("/businesses", response_model=list[BusinessResponse])
async def list_businesses(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(select(Business).order_by(Business.created_at.desc()))
    return result.scalars().all()


@router.get("/businesses/{business_id}", response_model=BusinessResponse)
async def get_business(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(404, "Negocio no encontrado")
    return business


@router.patch("/businesses/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    data: BusinessUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(select(Business).where(Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(404, "Negocio no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        if field in ("address", "city", "maps_url", "hours"):
            # Update settings
            s_result = await db.execute(
                select(BusinessSettings).where(BusinessSettings.business_id == business_id)
            )
            biz_settings = s_result.scalar_one_or_none()
            if biz_settings:
                setattr(biz_settings, field, value)
        else:
            setattr(business, field, value)

    await db.commit()
    await db.refresh(business)
    return business


# ──────────────────────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────────────────────

@router.post("/businesses/{business_id}/categories", response_model=LegalCategoryResponse, status_code=201)
async def create_category(
    business_id: str,
    data: LegalCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    category = LegalCategory(
        id=str(uuid.uuid4()),
        business_id=business_id,
        area=data.area,
        name=data.name,
        description=data.description,
        is_active=data.is_active,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.get("/businesses/{business_id}/categories", response_model=list[LegalCategoryResponse])
async def list_categories(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(LegalCategory).where(LegalCategory.business_id == business_id)
    )
    return result.scalars().all()


# ──────────────────────────────────────────────────────────────
# Services
# ──────────────────────────────────────────────────────────────

@router.post("/businesses/{business_id}/products", response_model=LegalServiceResponse, status_code=201)
async def create_product(
    business_id: str,
    data: LegalServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    service = LegalService(
        id=str(uuid.uuid4()),
        business_id=business_id,
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        base_price=data.price,
        estimated_timeframe=data.estimated_timeframe,
        requirements=data.requirements,
        is_available=data.is_available,
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("/businesses/{business_id}/products", response_model=list[LegalServiceResponse])
async def list_products(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(LegalService)
        .where(LegalService.business_id == business_id)
        .order_by(LegalService.name)
    )
    return result.scalars().all()


@router.patch("/businesses/{business_id}/products/{product_id}", response_model=LegalServiceResponse)
async def update_product(
    business_id: str,
    product_id: str,
    data: LegalServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(LegalService).where(LegalService.id == product_id, LegalService.business_id == business_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(404, "Servicio no encontrado")

    service.name = data.name
    service.description = data.description
    service.base_price = data.price
    service.is_available = data.is_available
    if data.category_id:
        service.category_id = data.category_id
    service.estimated_timeframe = data.estimated_timeframe
    service.requirements = data.requirements

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/businesses/{business_id}/products/{product_id}")
async def delete_product(
    business_id: str,
    product_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(LegalService).where(LegalService.id == product_id, LegalService.business_id == business_id)
    )
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(404, "Servicio no encontrado")

    await db.delete(service)
    await db.commit()
    return {"deleted": True, "id": product_id}


# ──────────────────────────────────────────────────────────────
# Bookings
# ──────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/bookings", response_model=list[BookingResponse])
async def list_bookings(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Booking)
        .where(Booking.business_id == business_id)
        .order_by(Booking.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/businesses/{business_id}/bookings/{booking_id}/status")
async def update_booking_status(
    business_id: str,
    booking_id: str,
    data: BookingStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.business_id == business_id)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(404, "Reserva no encontrada")

    booking.status = data.status
    await db.commit()
    return {"updated": True, "status": data.status}


# ──────────────────────────────────────────────────────────────
# Leads
# ──────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/leads")
async def list_leads(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Lead)
        .where(Lead.business_id == business_id)
        .order_by(Lead.created_at.desc())
    )
    leads_list = result.scalars().all()
    return [
        {
            "id": l.id,
            "phone": l.phone,
            "name": l.name,
            "first_intent": l.first_intent,
            "created_at": str(l.created_at),
        }
        for l in leads_list
    ]


# ──────────────────────────────────────────────────────────────
# Conversations
# ──────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/conversations")
async def list_conversations(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.business_id == business_id)
        .order_by(Conversation.created_at.desc())
        .limit(100)
    )
    convs = result.scalars().all()
    return [
        {
            "id": c.id,
            "customer_phone": c.customer_phone,
            "customer_name": c.customer_name,
            "status": c.status.value,
            "created_at": str(c.created_at),
        }
        for c in convs
    ]


@router.get("/businesses/{business_id}/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    business_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    msgs = result.scalars().all()
    return [
        {
            "direction": m.direction,
            "content": m.content,
            "intent": m.intent,
            "created_at": str(m.created_at),
        }
        for m in msgs
    ]


@router.patch("/businesses/{business_id}/conversations/{conversation_id}/close")
async def close_conversation(
    business_id: str,
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    """Cierra una conversación en handoff — permite reactivar automatización."""
    stmt = (
        update(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.business_id == business_id,
        )
        .values(status=ConversationStatus.ACTIVE)
    )
    await db.execute(stmt)
    await db.commit()
    return {"closed": True, "status": "active"}


# ──────────────────────────────────────────────────────────────
# Dashboard
# ──────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    business_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    leads_r = await db.execute(select(Lead).where(Lead.business_id == business_id))
    all_leads = leads_r.scalars().all()

    conv_r = await db.execute(
        select(Conversation).where(Conversation.business_id == business_id)
    )
    all_convs = conv_r.scalars().all()

    book_r = await db.execute(select(Booking).where(Booking.business_id == business_id))
    all_bookings = book_r.scalars().all()

    return DashboardResponse(
        total_conversations=len(all_convs),
        total_leads=len(all_leads),
        total_orders=0,
        total_revenue=0.0,
        pending_orders=0,
        pending_bookings=sum(1 for b in all_bookings if b.status == BookingStatus.PENDING),
    )


# ──────────────────────────────────────────────────────────────
# Quotes
# ──────────────────────────────────────────────────────────────

@router.get("/businesses/{business_id}/quotes", response_model=list[QuoteResponse])
async def list_quotes(
    business_id: str,
    status: QuoteStatus = None,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    stmt = select(Quote).where(Quote.business_id == business_id)
    if status:
        stmt = stmt.where(Quote.status == status)
    stmt = stmt.order_by(Quote.created_at.desc())
    result = await db.execute(stmt)
    quotes = result.scalars().all()

    out = []
    for q in quotes:
        items_r = await db.execute(select(QuoteItem).where(QuoteItem.quote_id == q.id))
        items = items_r.scalars().all()
        out.append(QuoteResponse(
            id=q.id,
            customer_phone=q.customer_phone,
            customer_name=q.customer_name,
            description=q.description,
            status=q.status,
            total=q.total or 0.0,
            items=[QuoteItemResponse(
                id=i.id,
                description=i.description,
                quantity=i.quantity,
                unit_price=i.unit_price,
                subtotal=round(i.quantity * i.unit_price, 2),
            ) for i in items],
        ))
    return out


@router.get("/businesses/{business_id}/quotes/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    business_id: str,
    quote_id: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id, Quote.business_id == business_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(404, "Cotización no encontrada")

    items_r = await db.execute(select(QuoteItem).where(QuoteItem.quote_id == q.id))
    items = items_r.scalars().all()
    return QuoteResponse(
        id=q.id,
        customer_phone=q.customer_phone,
        customer_name=q.customer_name,
        description=q.description,
        status=q.status,
        total=q.total or 0.0,
        items=[QuoteItemResponse(
            id=i.id,
            description=i.description,
            quantity=i.quantity,
            unit_price=i.unit_price,
            subtotal=round(i.quantity * i.unit_price, 2),
        ) for i in items],
    )


@router.post(
    "/businesses/{business_id}/quotes/{quote_id}/items",
    response_model=QuoteResponse,
    status_code=201,
)
async def add_quote_item(
    business_id: str,
    quote_id: str,
    data: QuoteItemCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id, Quote.business_id == business_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(404, "Cotización no encontrada")

    item = QuoteItem(
        id=str(uuid.uuid4()),
        quote_id=quote_id,
        description=data.description,
        quantity=data.quantity,
        unit_price=data.unit_price,
    )
    db.add(item)

    # Recalculate total
    items_r = await db.execute(select(QuoteItem).where(QuoteItem.quote_id == quote_id))
    existing = items_r.scalars().all()
    q.total = round(
        sum(i.quantity * i.unit_price for i in existing) + data.quantity * data.unit_price, 2
    )
    await db.commit()
    await db.refresh(q)

    all_items_r = await db.execute(select(QuoteItem).where(QuoteItem.quote_id == quote_id))
    all_items = all_items_r.scalars().all()
    return QuoteResponse(
        id=q.id,
        customer_phone=q.customer_phone,
        customer_name=q.customer_name,
        description=q.description,
        status=q.status,
        total=q.total or 0.0,
        items=[QuoteItemResponse(
            id=i.id,
            description=i.description,
            quantity=i.quantity,
            unit_price=i.unit_price,
            subtotal=round(i.quantity * i.unit_price, 2),
        ) for i in all_items],
    )


@router.patch("/businesses/{business_id}/quotes/{quote_id}/status", response_model=QuoteResponse)
async def update_quote_status(
    business_id: str,
    quote_id: str,
    data: QuoteStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    result = await db.execute(
        select(Quote).where(Quote.id == quote_id, Quote.business_id == business_id)
    )
    q = result.scalar_one_or_none()
    if not q:
        raise HTTPException(404, "Cotización no encontrada")

    q.status = data.status
    await db.commit()
    await db.refresh(q)

    items_r = await db.execute(select(QuoteItem).where(QuoteItem.quote_id == q.id))
    items = items_r.scalars().all()
    return QuoteResponse(
        id=q.id,
        customer_phone=q.customer_phone,
        customer_name=q.customer_name,
        description=q.description,
        status=q.status,
        total=q.total or 0.0,
        items=[QuoteItemResponse(
            id=i.id,
            description=i.description,
            quantity=i.quantity,
            unit_price=i.unit_price,
            subtotal=round(i.quantity * i.unit_price, 2),
        ) for i in items],
    )


# ──────────────────────────────────────────────────────────────
# Analytics
# ──────────────────────────────────────────────────────────────

from datetime import datetime, timedelta
from sqlalchemy import func


@router.get("/businesses/{business_id}/analytics")
async def get_analytics(
    business_id: str,
    period: str = "week",  # day | week | month
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_admin_key),
):
    now = datetime.utcnow()
    if period == "day":
        since = now - timedelta(days=1)
    elif period == "month":
        since = now - timedelta(days=30)
    else:  # week default
        since = now - timedelta(days=7)

    # Messages per day
    msgs_r = await db.execute(
        select(Message).where(
            Message.conversation_id.in_(
                select(Conversation.id).where(Conversation.business_id == business_id)
            ),
            Message.created_at >= since,
        )
    )
    all_msgs = msgs_r.scalars().all()
    msgs_by_day: dict[str, int] = {}
    for m in all_msgs:
        day = m.created_at.strftime("%Y-%m-%d")
        msgs_by_day[day] = msgs_by_day.get(day, 0) + 1

    # Intent distribution (from outbound messages that have intent set)
    intent_dist: dict[str, int] = {}
    inbound = [m for m in all_msgs if m.direction == "inbound" and m.intent]
    for m in inbound:
        intent_dist[m.intent] = intent_dist.get(m.intent, 0) + 1

    # Leads in period
    leads_r = await db.execute(
        select(Lead).where(Lead.business_id == business_id, Lead.created_at >= since)
    )
    period_leads = leads_r.scalars().all()

    lead_phones = {l.phone for l in period_leads}
    conversion_rate = 0.0

    return {
        "period": period,
        "since": since.isoformat(),
        "messages_by_day": msgs_by_day,
        "intent_distribution": intent_dist,
        "new_leads": len(period_leads),
        "new_orders": 0,
        "revenue": 0.0,
        "revenue_by_day": {},
        "conversion_rate_pct": conversion_rate,
        "top_products": [],
    }
