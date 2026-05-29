"""Helper: writes seed_demo.py with correct UTF-8 encoding."""
import io, os

SEED = '''\
"""
seed_demo.py - Carga datos de demo para Cafeteria Sabor y Encanto.

Uso:
    python seed_demo.py

Requiere que la DB este corriendo y las tablas creadas.
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

    print("Creando tablas...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # --- Negocio: Cafeteria Sabor y Encanto ----------------
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Sabor y Encanto",
            phone_number_id="DEMO_PHONE_NUMBER_ID",   # Reemplazar con el ID real de Meta
            whatsapp_token="DEMO_TOKEN",               # Reemplazar con el token real de Meta
            business_type=BusinessType.RESTAURANT,
            welcome_message=(
                "Hola! Bienvenido a Sabor y Encanto.\\n"
                "Te ayudo con nuestra carta, precios y pedidos.\\n"
                "Que se te antoja hoy?"
            ),
            human_support_phone="+56912345678",
            is_active=True,
        )
        db.add(business)

        biz_settings = BusinessSettings(
            id=str(uuid.uuid4()),
            business_id=business_id,
            address="Por definir",
            city="Santiago",
            maps_url=None,
            hours={
                "lunes":     "08:00-20:00",
                "martes":    "08:00-20:00",
                "miercoles": "08:00-20:00",
                "jueves":    "08:00-20:00",
                "viernes":   "08:00-21:00",
                "sabado":    "09:00-21:00",
                "domingo":   "09:00-18:00",
            },
            currency="CLP",
            currency_symbol="$",
        )
        db.add(biz_settings)

        # --- Categorias -----------------------------------------
        cat_names = [
            "Cafe Caliente",
            "Cafe de Especialidad",
            "Cafe Helado",
            "Sandwich Pan Tradicional",
            "Sandwich Pan Especial",
            "Completos y Hotdogs",
            "Bolleria y Pasteleria",
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

        # --- Productos ------------------------------------------
        # Tupla: (nombre, descripcion_base, precio_x1, precio_x2_o_None, categoria)
        # precio_x1 = precio unitario / tamano basico
        # precio_x2 = precio doble / tamano grande (se incluye en descripcion)
        raw_products = [
            # Cafe Caliente - Tradicional
            ("Cafe tradicional",     None,                                  800,  None,  "Cafe Caliente"),
            ("Te",                   None,                                 1000, None,  "Cafe Caliente"),
            ("Milo",                 None,                                 1000, None,  "Cafe Caliente"),
            ("Te con leche",         None,                                 1500, None,  "Cafe Caliente"),
            # Cafe de Especialidad
            ("Expreso",              "Simple o doble",                     1800, 2000,  "Cafe de Especialidad"),
            ("Te Twinings",          "En tetera",                          2000, None,  "Cafe de Especialidad"),
            ("Americano",            "Chico / Grande / Triple",            2200, 2700,  "Cafe de Especialidad"),
            ("Latte",                "Chico / Grande / Triple",            2500, 3000,  "Cafe de Especialidad"),
            ("Capuchino",            "Chico / Grande / Triple",            2500, 3000,  "Cafe de Especialidad"),
            ("Mocachino negro",      "Chocolate negro, tamano grande",     3200, None,  "Cafe de Especialidad"),
            ("Mocachino blanco",     "Chocolate blanco, tamano grande",    3200, None,  "Cafe de Especialidad"),
            ("Latte vainilla",       "Tamano grande",                      3200, None,  "Cafe de Especialidad"),
            ("Capuchino vainilla",   "Tamano grande",                      3200, None,  "Cafe de Especialidad"),
            # Cafe Helado
            ("Expreso naranja",      None,                                 3500, None,  "Cafe Helado"),
            ("Ice latte",            None,                                 4200, None,  "Cafe Helado"),
            ("Ice latte con sabor",  "Elige el sabor",                     4500, None,  "Cafe Helado"),
            ("Ice Matcha",           None,                                 4500, None,  "Cafe Helado"),
            ("Ice Chai",             None,                                 4800, None,  "Cafe Helado"),
            ("Frappe caramelo",      None,                                 5500, None,  "Cafe Helado"),
            ("Frappe Oreo",          None,                                 5500, None,  "Cafe Helado"),
            ("Milk shake",           None,                                 5500, None,  "Cafe Helado"),
            ("Afogatto",             None,                                 4000, None,  "Cafe Helado"),
            ("Cafe helado",          None,                                 5500, None,  "Cafe Helado"),
            ("Ice tea",              None,                                 2000, None,  "Cafe Helado"),
            # Sandwich Pan Tradicional (Marraqueta)
            ("Jamon queso",          "Marraqueta",                         1500, 2500,  "Sandwich Pan Tradicional"),
            ("Huevo",                "Marraqueta",                         2000, 3000,  "Sandwich Pan Tradicional"),
            ("Palta hass",           "Marraqueta",                         2000, 3000,  "Sandwich Pan Tradicional"),
            ("Ave mayo",             "Marraqueta",                         2000, 3000,  "Sandwich Pan Tradicional"),
            ("Palta tomate",         "Marraqueta",                         2000, 3000,  "Sandwich Pan Tradicional"),
            ("Palta tomate lechuga mayo", "Marraqueta",                    2200, 3300,  "Sandwich Pan Tradicional"),
            # Sandwich Pan Especial (Ciabatta / Integral / Blanco)
            ("Jamon queso especial",   "Ciabatta / Integral / Blanco",    3000, 5000,  "Sandwich Pan Especial"),
            ("Paila huevo",            "Ciabatta / Integral / Blanco",    3000, None,  "Sandwich Pan Especial"),
            ("Ave mayo especial",      "Ciabatta / Integral / Blanco",    3500, 5500,  "Sandwich Pan Especial"),
            ("Ave palta",              "Ciabatta / Integral / Blanco",    4000, 7000,  "Sandwich Pan Especial"),
            ("Churrasco queso",        "Ciabatta / Integral / Blanco",    4000, 6500,  "Sandwich Pan Especial"),
            ("Palta quesillo",         "Ciabatta / Integral / Blanco",    4000, 6000,  "Sandwich Pan Especial"),
            ("Palta huevo especial",   "Ciabatta / Integral / Blanco",    4000, 8000,  "Sandwich Pan Especial"),
            ("Churrasco italiano",     "Ciabatta / Integral / Blanco",    4500, 7000,  "Sandwich Pan Especial"),
            # Completos y Hotdogs
            ("Sopaipilla",           None,                                  400, None,  "Completos y Hotdogs"),
            ("Sopaipilla 3 unidades",None,                                 1000, None,  "Completos y Hotdogs"),
            ("Completo simple",      "Vienesa en pan",                     1800, 2500,  "Completos y Hotdogs"),
            ("Completo tomate mayo", "Con tomate y mayo",                  2000, 3000,  "Completos y Hotdogs"),
            ("Completo palta mayo",  "Con palta y mayo",                   2000, 3000,  "Completos y Hotdogs"),
            ("Completo palta tomate","Con palta y tomate",                 2000, 3000,  "Completos y Hotdogs"),
            ("Ass tomate mayo",      "As de as con tomate y mayo",         3000, 4500,  "Completos y Hotdogs"),
            ("Ass palta mayo",       "As de as con palta y mayo",          3000, 4500,  "Completos y Hotdogs"),
            ("Ass italiano",         "As de as italiano",                  3300, 4800,  "Completos y Hotdogs"),
            # Bolleria y Pasteleria
            ("Profiteroles",         None,                                 1000, None,  "Bolleria y Pasteleria"),
            ("Brownie",              None,                                 1500, None,  "Bolleria y Pasteleria"),
            ("Alfajor",              None,                                 1500, None,  "Bolleria y Pasteleria"),
            ("Queque tradicional",   None,                                 1500, None,  "Bolleria y Pasteleria"),
            ("Cupcake",              None,                                 1700, None,  "Bolleria y Pasteleria"),
            ("Queque sin azucar",    None,                                 3000, None,  "Bolleria y Pasteleria"),
            ("Kuchen",               "Porcion / Porcion doble",            3000, 4500,  "Bolleria y Pasteleria"),
            ("Torta del dia",        "Porcion / Porcion doble",            3500, 5500,  "Bolleria y Pasteleria"),
            # Bebidas y Jugos
            ("Agua mineral Benedictino", "Botella personal / familiar",   1200, 2000,  "Bebidas y Jugos"),
            ("Vaso de fruta",        "Personal / grande",                  1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Fanta",         "Personal / grande",                  1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Coca-Cola",     "Personal / grande",                  1500, 2500,  "Bebidas y Jugos"),
            ("Bebida Sprite",        "Personal / grande",                  1500, 2500,  "Bebidas y Jugos"),
            ("Jugo de frutas natural","Personal / grande",                 2500, 4000,  "Bebidas y Jugos"),
            ("Platano con leche",    "Personal / grande",                  3000, 4500,  "Bebidas y Jugos"),
        ]

        for name, base_desc, price_x1, price_x2, cat_name in raw_products:
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
        print(f"\\nDemo cargado exitosamente!")
        print(f"  Negocio    : Sabor y Encanto")
        print(f"  ID         : {business_id}")
        print(f"  Categorias : {len(categories)}")
        print(f"  Productos  : {total}")
        print(f"\\nIMPORTANTE: Actualiza phone_number_id y whatsapp_token en la DB")
        print(f"  o usa la API admin: PATCH /admin/businesses/{business_id}")


if __name__ == "__main__":
    asyncio.run(seed())
'''

dest = os.path.join(os.path.dirname(__file__), "seed_demo.py")
with io.open(dest, "w", encoding="utf-8") as f:
    f.write(SEED)
print(f"Written: {dest} ({len(SEED)} chars)")
