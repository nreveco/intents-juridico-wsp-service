"""
seed_demo.py - Carga datos de demo para Estudio Juridico

Uso:
    python seed_demo.py
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
    from app.db.models import (
        Business, BusinessSettings, LegalCategory, LegalService,
        BusinessType, LegalArea
    )

    print("Creando tablas...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # Negocio: Estudio Juridico Demo
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Estudio Juridico Demo",
            phone_number_id="DEMO_PHONE_NUMBER_ID",
            whatsapp_token="DEMO_TOKEN",
            business_type=BusinessType.LAW_FIRM,
            welcome_message="Hola! Bienvenido a nuestro estudio juridico. En que podemos ayudarte hoy?",
            human_support_phone="+56912345678",
            is_active=True,
        )
        db.add(business)

        biz_settings = BusinessSettings(
            id=str(uuid.uuid4()),
            business_id=business_id,
            address="Av. Libertador Bernardo O'Higgins 1234, Oficina 567",
            city="Santiago",
            maps_url="https://maps.google.com/?q=Santiago+Centro",
            hours={
                "lunes": "09:00-18:00",
                "martes": "09:00-18:00",
                "miercoles": "09:00-18:00",
                "jueves": "09:00-18:00",
                "viernes": "09:00-18:00",
            },
            currency="CLP",
            currency_symbol="$",
        )
        db.add(biz_settings)

        # Categorias Legales
        cat_penal = str(uuid.uuid4())
        cat_familia = str(uuid.uuid4())
        cat_civil = str(uuid.uuid4())

        db.add(LegalCategory(
            id=cat_penal,
            business_id=business_id,
            area=LegalArea.PENAL,
            name="Defensa Penal",
            description="Defensa en causas penales y delitos",
            is_active=True,
        ))

        db.add(LegalCategory(
            id=cat_familia,
            business_id=business_id,
            area=LegalArea.FAMILIA,
            name="Derecho de Familia",
            description="Divorcios, pensiones alimenticias, tuiciones",
            is_active=True,
        ))

        db.add(LegalCategory(
            id=cat_civil,
            business_id=business_id,
            area=LegalArea.CIVIL,
            name="Derecho Civil",
            description="Contratos, arrendamientos, indemnizaciones",
            is_active=True,
        ))

        # Servicios Legales
        services = [
            ("Defensa Ley 20.000", "Defensa penal en casos de trafico de drogas", 500000, "3-6 meses", cat_penal),
            ("Defensa VIF", "Defensa en casos de violencia intrafamiliar", 300000, "2-4 meses", cat_penal),
            ("Divorcio de Comun Acuerdo", "Tramitacion de divorcio consensuado", 200000, "1-2 meses", cat_familia),
            ("Pension Alimenticia", "Demanda o defensa en pension alimenticia", 250000, "2-3 meses", cat_familia),
            ("Redaccion de Contratos", "Contratos de arrendamiento, compraventa, etc.", 150000, "1-2 semanas", cat_civil),
        ]

        for name, desc, price, timeframe, cat_id in services:
            db.add(LegalService(
                id=str(uuid.uuid4()),
                business_id=business_id,
                category_id=cat_id,
                name=name,
                description=desc,
                base_price=price,
                estimated_timeframe=timeframe,
                is_available=True,
            ))

        await db.commit()

        print(f"\nDemo cargado exitosamente!")
        print(f"  Negocio    : Estudio Juridico Demo")
        print(f"  ID         : {business_id}")
        print(f"  Categorias : 3 (Penal, Familia, Civil)")
        print(f"  Servicios  : {len(services)}")
        print(f"\nIMPORTANTE: Actualiza phone_number_id y whatsapp_token en la DB")
        print(f"  API admin  : PATCH /admin/businesses/{{business_id}}")


if __name__ == "__main__":
    asyncio.run(seed())
