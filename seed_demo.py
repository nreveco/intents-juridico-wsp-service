"""
seed_demo.py â€” Carga datos de demo para CafeterÃ­a Sabor y Encanto.

Uso:
    python seed_demo.py

Requiere que la DB estÃ© corriendo y las tablas creadas (el servidor levanta las tablas automÃ¡ticamente).
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
    from app.db.database import init_db
    from app.db.models import Business, BusinessSettings, Category, Product, BusinessType

    print("âš™ï¸  Creando tablas...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # â”€â”€ Negocio: CafeterÃ­a Sabor y Encanto â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Sabor y Encanto",
            phone_number_id="DEMO_PHONE_NUMBER_ID",  # Reemplazar con ID real de Meta
            whatsapp_token="DEMO_TOKEN",              # Reemplazar con token real de Meta
            business_type=BusinessType.RESTAURANT,
            welcome_message=(
                "Hola! Bienvenido a *Sabor y Encanto*.\n"
                "Te ayudo con nuestra carta, precios y pedidos.\n"
                "Que se te antoja hoy?"
            ),
            human_support_phone="+56912345678",
            is_active=True,
        )
        db.add(business)

        biz_settings = BusinessSettings(
            id=str(uuid.uuid4()),
            business_id=business_id,
            address="Maipu 388",
            city="San Felipe",
            maps_url=None,
            hours={
                "lunes":     "08:30-18:00",
                "martes":    "08:30-18:00",
                "miércoles": "08:30-18:00",
                "jueves":    "08:30-18:00",
                "viernes":   "08:30-18:00",
                "sábado":    "09:00-18:00",
                "domingo":   "09:00-14:00",
            },
            currency="CLP",
            currency_symbol="$",
        )
        db.add(biz_settings)

        # â”€â”€ CategorÃ­as â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        cat_names = [
            "Café Caliente",
            "Café de Especialidad",
            "Café Helado",
            "Sándwich Pan Tradicional",
            "Sándwich Pan Especial",
            "Completos y Hotdogs",
            "Bollería y Pastelería",
            "Bebidas y Jugos",
        ]
        categories = {name: str(uuid.uuid4()) for name in cat_names}
        for cat_name, cat_id in categories.items():
            db.add(Category(
                id=cat_id,
                business_id=business_id,
                name=cat_name,
                is_active=True,
            ))

        # â”€â”€ Productos â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        # (nombre, descripciÃ³n, precio_x1, precio_x2_o_None, categorÃ­a)
        # precio mostrado es x1; si hay x2 se indica en descripciÃ³n
        raw_products = [
            # CafÃ© Caliente â€” Tradicional
            ("Café tradicional",    None,                               800,  None,  "Café Caliente"),
            ("Té",                  None,                               1000, None,  "Café Caliente"),
            ("Milo",                None,                               1000, None,  "Café Caliente"),
            ("Té con leche",        None,                               1500, None,  "Café Caliente"),
            # Café de Especialidad
            ("Expreso",             "Simple o doble",                   1800, 2000,  "Café de Especialidad"),
            ("Té Twinings",         "En tetera",                        2000, None,  "Café de Especialidad"),
            ("Americano",           "Chico / Grande / Triple",          2200, 2700,  "Café de Especialidad"),
            ("Latte",               "Chico / Grande / Triple",          2500, 3000,  "Café de Especialidad"),
            ("Capuchino",           "Chico / Grande / Triple",          2500, 3000,  "Café de Especialidad"),
            ("Mocachino negro",     "Chocolate negro, tamaño grande",   3200, None,  "Café de Especialidad"),
            ("Mocachino blanco",    "Chocolate blanco, tamaño grande",  3200, None,  "Café de Especialidad"),
            ("Latte vainilla",      "Tamaño grande",                    3200, None,  "Café de Especialidad"),
            ("Capuchino vainilla",  "Tamaño grande",                    3200, None,  "Café de Especialidad"),
            # Café Helado
            ("Expreso naranja",     None,                               3500, None,  "Café Helado"),
            ("Ice latte",           None,                               4200, None,  "Café Helado"),
            ("Ice latte con sabor", "Elige el sabor",                   4500, None,  "Café Helado"),
            ("Ice Matcha",          None,                               4500, None,  "Café Helado"),
            ("Ice Chai",            None,                               4800, None,  "Café Helado"),
            ("Frappe caramelo",     None,                               5500, None,  "Café Helado"),
            ("Frappe Oreo",         None,                               5500, None,  "Café Helado"),
            ("Milk shake",          None,                               5500, None,  "Café Helado"),
            ("Afogatto",            None,                               4000, None,  "Café Helado"),
            ("Café helado",         None,                               5500, None,  "Café Helado"),
            ("Ice tea",             None,                               2000, None,  "Café Helado"),
            # Sándwich Pan Tradicional / Marraqueta
            ("Jamón queso",         "Marraqueta",                       1500, 2500,  "Sándwich Pan Tradicional"),
            ("Huevo",               "Marraqueta",                       2000, 3000,  "Sándwich Pan Tradicional"),
            ("Palta hass",          "Marraqueta",                       2000, 3000,  "Sándwich Pan Tradicional"),
            ("Ave mayo",            "Marraqueta",                       2000, 3000,  "Sándwich Pan Tradicional"),
            ("Palta tomate",        "Marraqueta",                       2000, 3000,  "Sándwich Pan Tradicional"),
            ("Palta tomate lechuga mayo", "Marraqueta",                 2200, 3300,  "Sándwich Pan Tradicional"),
            # Sándwich Pan Especial (Ciabatta / Integral / Blanco)
            ("Jamón queso especial",    "Ciabatta / Integral / Blanco", 3000, 5000,  "Sándwich Pan Especial"),
            ("Paila huevo",             "Ciabatta / Integral / Blanco", 3000, None,  "Sándwich Pan Especial"),
            ("Ave mayo especial",       "Ciabatta / Integral / Blanco", 3500, 5500,  "Sándwich Pan Especial"),
            ("Ave palta",               "Ciabatta / Integral / Blanco", 4000, 7000,  "Sándwich Pan Especial"),
            ("Churrasco queso",         "Ciabatta / Integral / Blanco", 4000, 6500,  "Sándwich Pan Especial"),
            ("Palta quesillo",          "Ciabatta / Integral / Blanco", 4000, 6000,  "Sándwich Pan Especial"),
            ("Palta huevo",             "Ciabatta / Integral / Blanco", 4000, 8000,  "Sándwich Pan Especial"),
            ("Churrasco italiano",      "Ciabatta / Integral / Blanco", 4500, 7000,  "Sándwich Pan Especial"),
            # Completos y Hotdogs
            ("Sopaipilla",          None,                               400,  None,  "Completos y Hotdogs"),
            ("Sopaipilla 3 unidades", None,                             1000, None,  "Completos y Hotdogs"),
            ("Completo simple",     "Vienesa en pan",                   1800, 2500,  "Completos y Hotdogs"),
            ("Completo tomate mayo","Con tomate y mayo",                2000, 3000,  "Completos y Hotdogs"),
            ("Completo palta mayo", "Con palta y mayo",                 2000, 3000,  "Completos y Hotdogs"),
            ("Completo palta tomate","Con palta y tomate",              2000, 3000,  "Completos y Hotdogs"),
            ("Ass tomate mayo",     "As de as con tomate y mayo",       3000, 4500,  "Completos y Hotdogs"),
            ("Ass palta mayo",      "As de as con palta y mayo",        3000, 4500,  "Completos y Hotdogs"),
            ("Ass italiano",        "As de as italiano",                3300, 4800,  "Completos y Hotdogs"),
            # Bollería y Pastelería
            ("Profiteroles",        None,                               1000, None,  "Bollería y Pastelería"),
            ("Brownie",             None,                               1500, None,  "Bollería y Pastelería"),
            ("Alfajor",             None,                               1500, None,  "Bollería y Pastelería"),
            ("Queque tradicional",  None,                               1500, None,  "Bollería y Pastelería"),
            ("Cupcake",             None,                               1700, None,  "Bollería y Pastelería"),
            ("Queque sin azúcar",   None,                               3000, None,  "Bollería y Pastelería"),
            ("Kuchen",              "Porción / Porción doble",          3000, 4500,  "Bollería y Pastelería"),
            ("Torta del día",       "Porción / Porción doble",          3500, 5500,  "Bollería y Pastelería"),
            # Bebidas y Jugos
            ("Agua mineral Benedictino", "Botella personal / familiar", 1200, 2000,  "Bebidas y Jugos"),
            ("Vaso de fruta",       "Personal / grande",                1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Fanta",        "Personal / grande",                1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Coca-Cola",    "Personal / grande",                1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Sprite",       "Personal / grande",                1500, 2500,  "Bebidas y Jugos"),
            ("Jugo de frutas natural", "Personal / grande",             2500, 4000,  "Bebidas y Jugos"),
            ("Plátano con leche",   "Personal / grande",                3000, 4500,  "Bebidas y Jugos"),
        ]

        for name, base_desc, price_x1, price_x2, cat_name in raw_products:
            # Construir descripción incluyendo precio x2 si existe
            parts = []
            if base_desc:
                parts.append(base_desc)
            if price_x2:
                parts.append(f"x2: ${price_x2:,}".replace(",", "."))
            description = " | ".join(parts) if parts else None

            db.add(Product(
                id=str(uuid.uuid4()),
                business_id=business_id,
                category_id=categories[cat_name],
                name=name,
                description=description,
                price=price_x1,
                is_available=True,
            ))

        await db.commit()

        total = len(raw_products)
        print(f"\nDemo cargado exitosamente!")
        print(f"  Negocio    : Sabor y Encanto")
        print(f"  ID         : {business_id}")
        print(f"  Categorias : {len(categories)}")
        print(f"  Productos  : {total}")
        print(f"\nIMPORTANTE: Actualiza phone_number_id y whatsapp_token en la DB")
        print(f"  API admin  : PATCH /admin/businesses/{{business_id}}")


if __name__ == "__main__":
    asyncio.run(seed())

