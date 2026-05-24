"""
seed_demo.py — Carga datos de demo para una restaurante de prueba.

Uso:
    python seed_demo.py

Requiere que la DB esté corriendo y las tablas creadas (el servidor levanta las tablas automáticamente).
"""

import asyncio
import os
import uuid

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/automation_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed():
    # Import models aquí para evitar problemas de imports circulares
    from app.db.database import init_db
    from app.db.models import Business, BusinessSettings, Category, Product, BusinessType

    print("⚙️  Creando tablas...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Negocio demo: Restaurante ─────────────────────────
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Fuente de Soda El Rancho",
            phone_number_id="DEMO_PHONE_NUMBER_ID",  # Reemplazar con ID real de Meta
            whatsapp_token="DEMO_TOKEN",              # Reemplazar con token real de Meta
            business_type=BusinessType.RESTAURANT,
            welcome_message=(
                "¡Hola! 👋 Bienvenido a *Fuente de Soda El Rancho*.\n"
                "Puedo ayudarte con nuestro menú, precios, pedidos y reservas.\n"
                "¿En qué te puedo ayudar? 😊"
            ),
            human_support_phone="+56912345678",
            is_active=True,
        )
        db.add(business)

        biz_settings = BusinessSettings(
            id=str(uuid.uuid4()),
            business_id=business_id,
            address="Av. Providencia 1234, Local 5",
            city="Santiago",
            maps_url="https://maps.google.com/?q=Av+Providencia+1234+Santiago",
            hours={
                "lunes": "09:00-22:00",
                "martes": "09:00-22:00",
                "miércoles": "09:00-22:00",
                "jueves": "09:00-23:00",
                "viernes": "09:00-23:00",
                "sábado": "10:00-23:00",
                "domingo": "10:00-21:00",
            },
            currency="CLP",
            currency_symbol="$",
        )
        db.add(biz_settings)

        # ── Categorías ─────────────────────────────────────────
        categories = {
            "Completos y Sándwiches": str(uuid.uuid4()),
            "Hamburguesas": str(uuid.uuid4()),
            "Bebidas": str(uuid.uuid4()),
            "Postres": str(uuid.uuid4()),
        }

        for cat_name, cat_id in categories.items():
            db.add(Category(
                id=cat_id,
                business_id=business_id,
                name=cat_name,
                is_active=True,
            ))

        # ── Productos ──────────────────────────────────────────
        products = [
            # Completos
            ("Completo Italiano", "Con tomate, mayo y palta", 2800, "Completos y Sándwiches"),
            ("Completo Dinámico", "Con mayo, sauerkraut y salsa americana", 2600, "Completos y Sándwiches"),
            ("Completo Doble", "Doble vienesa, tomate, mayo y palta", 3500, "Completos y Sándwiches"),
            ("Churrasco Italiano", "Lomo cerdito, tomate, mayo y palta", 4200, "Completos y Sándwiches"),
            ("Sándwich Ave Palta", "Pollo a la plancha, palta, tomate y mayo", 3900, "Completos y Sándwiches"),
            # Hamburguesas
            ("Hamburguesa Clásica", "Carne, queso cheddar, lechuga, tomate y mayo", 4500, "Hamburguesas"),
            ("Hamburguesa Doble", "Doble carne, doble queso, bacon y mayo", 5900, "Hamburguesas"),
            ("Hamburguesa Pollo Crispy", "Pollo apanado, coleslaw y salsa BBQ", 4800, "Hamburguesas"),
            # Bebidas
            ("Coca-Cola 350ml", None, 1200, "Bebidas"),
            ("Jugo Natural Naranja", "Naranja exprimida al momento", 1800, "Bebidas"),
            ("Agua Mineral 500ml", None, 900, "Bebidas"),
            ("Café Americano", "Café de grano molido", 1500, "Bebidas"),
            # Postres
            ("Helado 1 Bola", "Sabores: vainilla, chocolate, frutilla", 1200, "Postres"),
            ("Torta de Mil Hojas", "Porción individual con crema pastelera", 2200, "Postres"),
        ]

        for name, desc, price, cat_name in products:
            db.add(Product(
                id=str(uuid.uuid4()),
                business_id=business_id,
                category_id=categories[cat_name],
                name=name,
                description=desc,
                price=price,
                is_available=True,
            ))

        await db.commit()

        print(f"\n✅ Demo cargado exitosamente!")
        print(f"   Negocio: Fuente de Soda El Rancho")
        print(f"   ID: {business_id}")
        print(f"   Productos: {len(products)}")
        print(f"\n⚠️  IMPORTANTE: Actualiza phone_number_id y whatsapp_token en la DB")
        print(f"   o usa la API admin: PATCH /admin/businesses/{business_id}")
        print(f"\n🚀 Levanta el servidor: uvicorn app.main:app --reload")
        print(f"   Docs: http://localhost:8000/docs")


if __name__ == "__main__":
    asyncio.run(seed())
