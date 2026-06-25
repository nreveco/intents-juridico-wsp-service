"""
Script para verificar que todo el sistema funcione correctamente
"""
import asyncio
import sys
from app.config import settings
from app.db.database import AsyncSessionLocal
from sqlalchemy import text, select
from app.db.models import Business, LegalService, LegalCategory


async def test_system():
    """Verifica todos los componentes del sistema"""
    
    print("\n" + "=" * 70)
    print("🧪 TEST COMPLETO DEL SISTEMA")
    print("=" * 70 + "\n")
    
    errors = []
    warnings = []
    
    # 1. Configuración
    print("1️⃣  Verificando configuración...")
    if not settings.database_url:
        errors.append("DATABASE_URL no configurada")
    else:
        print(f"   ✅ DATABASE_URL: configurada")
    
    if not settings.whatsapp_token or settings.whatsapp_token == "":
        warnings.append("WHATSAPP_TOKEN no configurada (requerida para producción)")
    else:
        print(f"   ✅ WHATSAPP_TOKEN: configurada")
    
    if not settings.ollama_base_url:
        errors.append("OLLAMA_BASE_URL no configurada")
    else:
        print(f"   ✅ OLLAMA_BASE_URL: {settings.ollama_base_url}")
    
    print()
    
    # 2. Base de datos
    print("2️⃣  Verificando base de datos...")
    try:
        async with AsyncSessionLocal() as session:
            # Test conexión
            await session.execute(text("SELECT 1"))
            print(f"   ✅ Conexión a base de datos: OK")
            
            # Verificar tablas principales
            tables_to_check = [
                'businesses', 'business_settings', 'legal_categories', 
                'legal_services', 'conversations', 'bookings', 'case_inquiries'
            ]
            
            for table in tables_to_check:
                result = await session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                count = result.scalar()
                print(f"   ✅ Tabla '{table}': {count} registros")
            
    except Exception as e:
        errors.append(f"Error en base de datos: {e}")
        print(f"   ❌ Error: {e}")
    
    print()
    
    # 3. Modelos SQLAlchemy
    print("3️⃣  Verificando modelos...")
    try:
        async with AsyncSessionLocal() as session:
            # Probar query con ORM
            result = await session.execute(
                select(Business).limit(1)
            )
            business = result.scalar_one_or_none()
            
            if business:
                print(f"   ✅ Modelo Business: OK")
                print(f"      • ID: {business.id}")
                print(f"      • Nombre: {business.name}")
                print(f"      • Tipo: {business.business_type}")
                
                # Verificar relaciones
                result = await session.execute(
                    select(LegalCategory).where(LegalCategory.business_id == business.id)
                )
                categories = result.scalars().all()
                print(f"   ✅ Categorías legales: {len(categories)}")
                
                result = await session.execute(
                    select(LegalService).where(LegalService.business_id == business.id)
                )
                services = result.scalars().all()
                print(f"   ✅ Servicios legales: {len(services)}")
            else:
                warnings.append("No hay datos de demo (ejecutar seed_demo.py)")
                print(f"   ⚠️  No hay negocios registrados")
                
    except Exception as e:
        errors.append(f"Error en modelos: {e}")
        print(f"   ❌ Error: {e}")
    
    print()
    
    # 4. Ollama (solo si está configurado)
    print("4️⃣  Verificando Ollama...")
    if settings.ollama_base_url:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Intentar conectar a Ollama
                url = settings.ollama_base_url.replace('/v1', '') + '/api/tags'
                response = await client.get(url)
                
                if response.status_code == 200:
                    print(f"   ✅ Ollama accesible: {url}")
                    data = response.json()
                    models = data.get('models', [])
                    print(f"   ✅ Modelos disponibles: {len(models)}")
                    for model in models[:3]:  # Mostrar primeros 3
                        print(f"      • {model.get('name', 'unknown')}")
                else:
                    warnings.append(f"Ollama no responde (status {response.status_code})")
                    print(f"   ⚠️  Ollama responde con status {response.status_code}")
                    
        except Exception as e:
            warnings.append(f"Ollama no accesible: {e}")
            print(f"   ⚠️  No se pudo conectar: {e}")
    else:
        warnings.append("OLLAMA_BASE_URL no configurada")
        print(f"   ⚠️  OLLAMA_BASE_URL no configurada")
    
    print()
    
    # Resumen
    print("=" * 70)
    if not errors:
        print("✅ SISTEMA FUNCIONANDO CORRECTAMENTE")
        if warnings:
            print(f"\n⚠️  Advertencias ({len(warnings)}):")
            for warning in warnings:
                print(f"   • {warning}")
    else:
        print("❌ ERRORES DETECTADOS")
        for error in errors:
            print(f"   • {error}")
        if warnings:
            print(f"\n⚠️  Advertencias adicionales:")
            for warning in warnings:
                print(f"   • {warning}")
    
    print("=" * 70 + "\n")
    
    return len(errors) == 0


if __name__ == "__main__":
    success = asyncio.run(test_system())
    sys.exit(0 if success else 1)
