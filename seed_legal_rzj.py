"""
seed_legal_rzj.py — Carga datos iniciales para Estudio Jurídico Mediaciones RJZ

Este seed prepara el sistema para un estudio jurídico especializado en:
- Derecho de Familia (custodia, mediación, pensión alimenticia, regulación de visitas)

Basado en análisis de preguntas frecuentes y casos reales del estudio.

Uso:
    python seed_legal_rzj.py

Requiere que la DB esté corriendo y las tablas creadas.
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
        Business, BusinessSettings, BusinessType,
        LegalCategory, LegalService, LegalArea, FeeStructure
    )

    print("⚖️  Inicializando base de datos para Mediaciones RJZ...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Negocio: Mediaciones RJZ ────────────────────────────────────────
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Mediaciones RJZ",
            phone_number_id="1158066464056590",  # ID real usado por el webhook
            whatsapp_token="DEMO_TOKEN",              # ⚠️ Reemplazar con Token real de Meta
            business_type=BusinessType.LAW_FIRM,      # ✅ Ahora usamos LAW_FIRM
            welcome_message=(
                "¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️\n\n"
                "Somos un estudio jurídico especializado en Derecho de Familia:\n"
                "• Custodia de menores\n"
                "• Pensión alimenticia\n"
                "• Regulación de visitas y mediación familiar\n\n"
                "Estamos aquí para ayudarte a encontrar una solución rápida y cercana. ¿En qué podemos asesorarte hoy?"
            ),
            human_support_phone="+56912345678",  # ⚠️ Número del abogado responsable
            is_active=True,
        )
        db.add(business)

        # ── Configuración del Negocio ───────────────────────────────────────
        biz_settings = BusinessSettings(
            id=str(uuid.uuid4()),
            business_id=business_id,
            address="Av. Libertador Bernardo O'Higgins 1234, Oficina 501",
            city="Santiago",
            maps_url="https://maps.google.com/?q=Mediaciones+RJZ+Santiago",
            hours={
                "lunes":     "09:00-18:00",
                "martes":    "09:00-18:00",
                "miércoles": "09:00-18:00",
                "jueves":    "09:00-18:00",
                "viernes":   "09:00-18:00",
                "sábado":    "10:00-14:00",  # Medio día sábado
                "domingo":   "Cerrado",
            },
            currency="CLP",
            currency_symbol="$",
        )
        db.add(biz_settings)

        # ── Categorías Legales (usando LegalCategory) ────────────
        categories_data = [
            {
                "area": LegalArea.FAMILIA,
                "name": "Derecho de Familia",
                "description": (
                    "Mediación familiar, custodia de menores, pensión alimenticia, "
                    "regulación de visitas y acuerdos de convivencia."
                )
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat_id = str(uuid.uuid4())
            categories[cat_data["name"]] = cat_id
            db.add(LegalCategory(
                id=cat_id,
                business_id=business_id,
                area=cat_data["area"],
                name=cat_data["name"],
                description=cat_data["description"],
                is_active=True,
            ))

        # ── Servicios Legales (usando LegalService) ─────────────────────────────────
        # Cada servicio tiene:
        # - name, description
        # - base_price (orientativo, puede variar según complejidad)
        # - estimated_timeframe (duración típica del proceso)
        # - requirements (requisitos generales)

        services = [
            (
                "Mediación Familiar",
                (
                    "Proceso de mediación obligatoria para alimentos, custodia y visitas. "
                    "Facilitamos acuerdos entre las partes evitando litigio."
                ),
                300000,
                "1-2 meses",
                "Requisito previo a demandas de familia. Incluye sesiones de mediación.",
                "Derecho de Familia"
            ),
            (
                "Custodia y Cuidado Personal",
                (
                    "Demanda o defensa en casos de custodia de menores. "
                    "Incluye: mediación previa, demanda judicial, peritaje psicosocial, "
                    "audiencias preparatorias y de juicio."
                ),
                800000,
                "4-8 meses",
                "Requiere mediación previa. Puede incluir peritaje psicológico del menor.",
                "Derecho de Familia"
            ),
            (
                "Pensión de Alimentos",
                (
                    "Demanda de pensión alimenticia para hijos o defensa. "
                    "Incluye: cálculo de pensión, mediación, audiencias."
                ),
                400000,
                "3-5 meses",
                "Se puede solicitar pensión provisoria urgente. Requiere mediación previa.",
                "Derecho de Familia"
            ),
            (
                "Regulación de Visitas (Relación Directa y Regular)",
                (
                    "Establecimiento o modificación del régimen de visitas. "
                    "Incluye: mediación, demanda judicial si no hay acuerdo."
                ),
                350000,
                "2-4 meses",
                "Busca establecer relación estable entre padre/madre e hijo.",
                "Derecho de Familia"
            ),
        ]

        total_services = 0
        for name, description, base_price, timeframe, requirements, category_name in services:
            db.add(LegalService(
                id=str(uuid.uuid4()),
                business_id=business_id,
                category_id=categories[category_name],
                name=name,
                description=description,
                base_price=base_price,
                estimated_timeframe=timeframe,
                requirements=requirements,
                is_available=True,
            ))
            total_services += 1

        await db.commit()

        # ── Resumen ─────────────────────────────────────────────────────────
        print("\n" + "="*70)
        print("✅ SEED COMPLETADO EXITOSAMENTE - SISTEMA LEGAL")
        print("="*70)
        print(f"📋 Negocio creado:")
        print(f"   Nombre    : Mediaciones RJZ")
        print(f"   ID        : {business_id}")
        print(f"   Tipo      : LAW_FIRM (Estudio Jurídico)")
        print(f"   Ciudad    : Santiago")
        print(f"   Contacto  : +56912345678")
        print(f"\n⚖️  Áreas legales : {len(categories)}")
        for cat_name in categories.keys():
            print(f"   • {cat_name}")
        print(f"\n📦 Servicios legales : {total_services}")
        print(f"\n✅ MODELOS ACTUALIZADOS:")
        print(f"   • Business → business_type=LAW_FIRM")
        print(f"   • LegalCategory (reemplaza Category)")
        print(f"   • LegalService (reemplaza Product)")
        print(f"   • Con campos: estimated_timeframe, requirements")
        print(f"\n⚠️  PRÓXIMOS PASOS:")
        print(f"   1. Completar PASO 5: webhook.py con función _route_intent legal")
        print(f"   2. Actualizar phone_number_id y whatsapp_token con valores REALES")
        print(f"      Usar API admin: PATCH /admin/businesses/{business_id}")
        print(f"   3. Probar con mensajes de prueba:")
        print(f"      • 'Hola, quiero información'")
        print(f"      • '¿Ven temas penales?'")
        print(f"      • 'Tengo un caso de tráfico de drogas'")
        print(f"      • '¿Cuánto cobran?'")
        print(f"   4. Ejecutar migraciones de base de datos si es necesario")
        print("\n" + "="*70)
        print("📖 Consulta RESUMEN_EJECUTIVO_RJZ.md para el roadmap completo")
        print("📖 Ver COMPLETAR_PASO_5_MANUAL.md para finalizar webhook.py")
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed())
