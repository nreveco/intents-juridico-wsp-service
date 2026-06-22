"""
seed_legal_rzj.py — Carga datos iniciales para Estudio Jurídico Mediaciones RJZ

Este seed prepara el sistema para un estudio jurídico especializado en:
- Derecho Penal (Ley 20.000, VIF, delitos contra las personas, beneficios penitenciarios)
- Derecho de Familia (custodia, mediación, pensión alimenticia)
- Derecho Civil (cobranza, compraventas, contratos)

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
    from app.db.models import Business, BusinessSettings, Category, Product, BusinessType

    print("⚖️  Inicializando base de datos para Mediaciones RJZ...")
    await init_db()

    async with AsyncSessionLocal() as db:
        # ── Negocio: Mediaciones RJZ ────────────────────────────────────────
        business_id = str(uuid.uuid4())

        business = Business(
            id=business_id,
            name="Mediaciones RJZ",
            phone_number_id="DEMO_PHONE_NUMBER_ID",  # ⚠️ Reemplazar con Phone Number ID real de Meta
            whatsapp_token="DEMO_TOKEN",              # ⚠️ Reemplazar con Token real de Meta
            business_type=BusinessType.OTHER,         # Usamos OTHER hasta agregar LAW_FIRM al enum
            welcome_message=(
                "¡Hola! Bienvenido a *Mediaciones RJZ* ⚖️\n\n"
                "Somos un estudio jurídico especializado en:\n"
                "• Derecho Penal (defensa, beneficios penitenciarios)\n"
                "• Derecho de Familia (VIF, custodia, mediación)\n"
                "• Derecho Civil (contratos, cobros, propiedades)\n\n"
                "Estamos aquí para ayudarte 24/7. ¿En qué podemos asesorarte hoy?"
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

        # ── Categorías Legales (usando tabla Category existente) ────────────
        # NOTA: En producción, esto debería ser LegalCategory con más campos
        categories_data = [
            {
                "name": "Derecho Penal ⚖️",
                "description": (
                    "Defensa penal en todas las etapas del proceso. "
                    "Especialistas en Ley 20.000, VIF, delitos contra las personas, "
                    "beneficios penitenciarios y recursos de apelación."
                )
            },
            {
                "name": "Derecho de Familia 👨‍👩‍👧",
                "description": (
                    "Mediación familiar, custodia de menores, pensión alimenticia, "
                    "regulación de visitas, y casos de VIF con peritaje psicosocial."
                )
            },
            {
                "name": "Derecho Civil 📋",
                "description": (
                    "Contratos, compraventa de inmuebles, cobranza judicial, "
                    "escrituras públicas y asesoría en trámites civiles."
                )
            },
        ]

        categories = {}
        for cat_data in categories_data:
            cat_id = str(uuid.uuid4())
            categories[cat_data["name"]] = cat_id
            db.add(Category(
                id=cat_id,
                business_id=business_id,
                name=cat_data["name"],
                description=cat_data["description"],
                is_active=True,
            ))

        # ── "Productos" (Servicios Legales) ─────────────────────────────────
        # NOTA: Usamos tabla Product existente temporalmente.
        # En producción esto debe ser LegalService con campos específicos:
        # - typical_duration, complexity, requires_evaluation, base_info, etc.
        #
        # El campo "price" aquí representa el precio BASE de referencia (no final).
        # Los honorarios reales varían según complejidad del caso.

        services = [
            # ─── DERECHO PENAL ──────────────────────────────────────────────
            (
                "Defensa Penal - Ley 20.000 (Drogas)",
                (
                    "Defensa especializada en casos de tráfico y microtráfico de drogas. "
                    "Incluye: análisis de pruebas, estrategia de defensa, audiencias, "
                    "negociación con fiscalía. "
                    "Duración típica: 3-6 meses. "
                    "Casos atendidos: Art. 3° (microtráfico), Art. 4° (tráfico simple), "
                    "Art. 5° (tráfico agravado). "
                    "⚠️ Evaluación gratuita del caso."
                ),
                800000,  # Precio base referencial
                "Derecho Penal ⚖️"
            ),
            (
                "Defensa en VIF (Violencia Intrafamiliar)",
                (
                    "Defensa en casos de violencia intrafamiliar. "
                    "Incluye: representación en audiencias, coordinación con peritaje psicosocial, "
                    "estrategia de defensa o acuerdos reparatorios. "
                    "Duración típica: 2-4 meses. "
                    "Atendemos tanto a víctimas como a imputados."
                ),
                600000,
                "Derecho Penal ⚖️"
            ),
            (
                "Delitos contra las Personas",
                (
                    "Defensa en homicidio, lesiones, amenazas y otros delitos contra las personas. "
                    "Incluye: estrategia de defensa, recursos, audiencias. "
                    "Duración típica: 4-8 meses según gravedad. "
                    "Atención urgente para casos con prisión preventiva."
                ),
                1200000,
                "Derecho Penal ⚖️"
            ),
            (
                "Beneficios Penitenciarios",
                (
                    "Tramitación de libertad condicional, reclusión nocturna, "
                    "salidas dominicales y otros beneficios de Ley 18.216. "
                    "Incluye: evaluación de requisitos, preparación de antecedentes, "
                    "audiencia ante el juez. "
                    "Duración: 1-2 meses. "
                    "⚠️ Requisitos: cumplir parte de condena, no tener sanciones."
                ),
                450000,
                "Derecho Penal ⚖️"
            ),
            (
                "Apelaciones y Recursos Penales",
                (
                    "Recursos de apelación, nulidad y amparo en materia penal. "
                    "Incluye: análisis de sentencia, fundamentación del recurso, "
                    "audiencia ante Corte de Apelaciones. "
                    "Duración: 2-4 meses."
                ),
                700000,
                "Derecho Penal ⚖️"
            ),
            (
                "Calumnias e Injurias",
                (
                    "Querella o defensa en casos de calumnias e injurias. "
                    "Común en contextos de VIF o conflictos laborales/familiares. "
                    "Incluye: redacción de querella, representación en audiencias. "
                    "Duración: 3-5 meses."
                ),
                500000,
                "Derecho Penal ⚖️"
            ),
            
            # ─── DERECHO DE FAMILIA ─────────────────────────────────────────
            (
                "Mediación Familiar",
                (
                    "Proceso de mediación obligatoria para alimentos, custodia y visitas. "
                    "Facilitamos acuerdos entre las partes evitando litigio. "
                    "Incluye: sesiones de mediación, redacción de acuerdos. "
                    "Duración: 1-2 meses. "
                    "Requisito previo a demandas de familia."
                ),
                300000,
                "Derecho de Familia 👨‍👩‍👧"
            ),
            (
                "Custodia y Cuidado Personal",
                (
                    "Demanda o defensa en casos de custodia de menores. "
                    "Incluye: mediación previa, demanda judicial, peritaje psicosocial, "
                    "audiencias preparatorias y de juicio. "
                    "Duración: 4-8 meses."
                ),
                800000,
                "Derecho de Familia 👨‍👩‍👧"
            ),
            (
                "Pensión de Alimentos",
                (
                    "Demanda de pensión alimenticia para hijos o defensa. "
                    "Incluye: cálculo de pensión, mediación, audiencias. "
                    "Duración: 3-5 meses. "
                    "Se puede solicitar pensión provisoria urgente."
                ),
                400000,
                "Derecho de Familia 👨‍👩‍👧"
            ),
            (
                "Regulación de Visitas (Relación Directa y Regular)",
                (
                    "Establecimiento o modificación del régimen de visitas. "
                    "Incluye: mediación, demanda judicial si no hay acuerdo. "
                    "Duración: 2-4 meses."
                ),
                350000,
                "Derecho de Familia 👨‍👩‍👧"
            ),

            # ─── DERECHO CIVIL ──────────────────────────────────────────────
            (
                "Cobranza Judicial",
                (
                    "Cobranza de deudas mediante juicio ejecutivo o cobranza ordinaria. "
                    "Incluye: demanda, embargo, remate si es necesario. "
                    "Duración: 4-12 meses según complejidad. "
                    "Honorarios variables según monto a cobrar."
                ),
                400000,  # Puede ser % del monto recuperado
                "Derecho Civil 📋"
            ),
            (
                "Compraventa de Inmuebles - Escrituración",
                (
                    "Redacción y tramitación de escrituras de compraventa. "
                    "Incluye: revisión de títulos, inscripción en Conservador de Bienes Raíces. "
                    "Duración: 1-2 meses. "
                    "⚠️ No incluye impuestos ni tasas notariales (corren por cuenta del cliente)."
                ),
                350000,
                "Derecho Civil 📋"
            ),
            (
                "Regularización de Propiedades",
                (
                    "Tramitación de posesión efectiva, inscripciones pendientes, "
                    "saneamiento de títulos. "
                    "Incluye: búsqueda de antecedentes, gestiones ante Conservador. "
                    "Duración: 3-6 meses."
                ),
                600000,
                "Derecho Civil 📋"
            ),
            (
                "Redacción de Contratos",
                (
                    "Redacción y revisión de contratos (arriendo, compraventa, prestación de servicios). "
                    "Incluye: análisis de cláusulas, asesoría legal. "
                    "Entrega: 1-2 semanas."
                ),
                200000,
                "Derecho Civil 📋"
            ),

            # ─── OTROS SERVICIOS ────────────────────────────────────────────
            (
                "Consulta Legal Presencial",
                (
                    "Reunión presencial de 1 hora con abogado especialista. "
                    "Evaluación de tu caso, estrategia legal recomendada, "
                    "presupuesto detallado. "
                    "⚠️ PRIMERA CONSULTA GRATUITA para nuevos clientes."
                ),
                50000,  # Consultas posteriores tienen costo
                "Derecho Penal ⚖️"  # Se puede asociar a cualquier categoría
            ),
            (
                "Traslado de Imputados",
                (
                    "Coordinación de traslado de imputados detenidos a audiencias u otras diligencias. "
                    "Incluye: gestión con Gendarmería, seguimiento del traslado. "
                    "⚠️ Servicio de emergencia - disponibilidad inmediata."
                ),
                400000,
                "Derecho Penal ⚖️"
            ),
        ]

        total_services = 0
        for name, description, base_price, category_name in services:
            db.add(Product(
                id=str(uuid.uuid4()),
                business_id=business_id,
                category_id=categories[category_name],
                name=name,
                description=description,
                price=base_price,
                is_available=True,
            ))
            total_services += 1

        await db.commit()

        # ── Resumen ─────────────────────────────────────────────────────────
        print("\n" + "="*70)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("="*70)
        print(f"📋 Negocio creado:")
        print(f"   Nombre    : Mediaciones RJZ")
        print(f"   ID        : {business_id}")
        print(f"   Tipo      : Estudio Jurídico")
        print(f"   Ciudad    : Santiago")
        print(f"   Contacto  : +56912345678")
        print(f"\n⚖️  Áreas legales : {len(categories)}")
        for cat_name in categories.keys():
            print(f"   • {cat_name}")
        print(f"\n📦 Servicios legales : {total_services}")
        print(f"\n⚠️  PRÓXIMOS PASOS:")
        print(f"   1. Actualizar phone_number_id y whatsapp_token con valores REALES")
        print(f"   2. Usar API admin: PATCH /admin/businesses/{business_id}")
        print(f"   3. Modificar intents en app/intents/definitions.py para contexto legal")
        print(f"   4. Adaptar prompts en app/prompts/templates.py")
        print(f"   5. Crear servicios: legal_services.py, case_inquiries.py, fee_info.py")
        print("\n" + "="*70)
        print("📖 Consulta ANALISIS_ESTUDIO_JURIDICO.md para el roadmap completo")
        print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(seed())
