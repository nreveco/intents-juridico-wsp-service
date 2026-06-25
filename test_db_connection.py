"""
Script para verificar la conexión a la base de datos de Railway
"""
import asyncio
import sys
from sqlalchemy import text
from app.config import settings
from app.db.database import engine, AsyncSessionLocal
from app.db.models import Business


async def test_connection():
    """Verifica la conexión y estructura de la base de datos"""
    
    print("=" * 70)
    print("🔍 VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
    print("=" * 70)
    print()
    
    # 1. Verificar configuración
    print("📋 Configuración actual:")
    print(f"  • DATABASE_URL: {settings.database_url[:50]}...")
    print(f"  • ENVIRONMENT: {settings.environment}")
    print(f"  • IS_PRODUCTION: {settings.is_production}")
    print()
    
    try:
        # 2. Test de conexión básica
        print("🔌 Probando conexión básica...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"  ✅ Conexión exitosa!")
            print(f"  • PostgreSQL: {version.split(',')[0]}")
        print()
        
        # 3. Verificar tablas existentes
        print("📊 Verificando tablas en la base de datos...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"  ✅ Se encontraron {len(tables)} tablas:")
                for table in tables:
                    print(f"     • {table}")
            else:
                print("  ⚠️  No se encontraron tablas!")
                print("     Ejecuta railway-init.sql en Railway")
        print()
        
        # 4. Verificar enum types
        print("🔖 Verificando tipos ENUM...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT typname 
                FROM pg_type 
                WHERE typtype = 'e'
                ORDER BY typname
            """))
            enums = [row[0] for row in result]
            
            if enums:
                print(f"  ✅ Se encontraron {len(enums)} enums:")
                for enum in enums:
                    print(f"     • {enum}")
            else:
                print("  ⚠️  No se encontraron enums!")
        print()
        
        # 5. Verificar datos de ejemplo
        print("📦 Verificando datos de ejemplo...")
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT COUNT(*) FROM businesses"))
            count = result.scalar()
            
            if count > 0:
                print(f"  ✅ Se encontraron {count} negocios registrados")
                
                # Obtener info del negocio demo
                result = await session.execute(text("""
                    SELECT id, name, business_type, phone_number_id 
                    FROM businesses 
                    LIMIT 1
                """))
                business = result.first()
                if business:
                    print(f"     • ID: {business[0]}")
                    print(f"     • Nombre: {business[1]}")
                    print(f"     • Tipo: {business[2]}")
                    print(f"     • Phone ID: {business[3]}")
            else:
                print("  ℹ️  No hay negocios registrados (usar seed_demo.py)")
        print()
        
        # 6. Verificar índices
        print("📇 Verificando índices...")
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                AND indexname LIKE 'idx_%'
                ORDER BY indexname
            """))
            indexes = [row[0] for row in result]
            
            if indexes:
                print(f"  ✅ Se encontraron {len(indexes)} índices personalizados")
            else:
                print("  ℹ️  No hay índices personalizados")
        print()
        
        # 7. Verificar permisos
        print("🔐 Verificando permisos de usuario...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"  • Usuario conectado: {user}")
            
            # Probar escritura
            try:
                await conn.execute(text("""
                    CREATE TEMP TABLE test_write_permission (id INT);
                    DROP TABLE test_write_permission;
                """))
                print(f"  ✅ Permisos de escritura: OK")
            except Exception as e:
                print(f"  ⚠️  Error en permisos de escritura: {e}")
        print()
        
        print("=" * 70)
        print("✅ VERIFICACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print()
        print("🚀 El sistema está listo para usar con Railway!")
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERROR EN LA VERIFICACIÓN")
        print("=" * 70)
        print()
        print(f"Error: {type(e).__name__}")
        print(f"Detalle: {str(e)}")
        print()
        print("Posibles causas:")
        print("  1. DATABASE_URL incorrecta o no configurada")
        print("  2. Base de datos no accesible desde esta ubicación")
        print("  3. Tablas no creadas (ejecutar railway-init.sql)")
        print("  4. Permisos insuficientes del usuario de BD")
        print()
        print("Solución:")
        print("  1. Verifica que DATABASE_URL esté en .env")
        print("  2. Ejecuta railway-init.sql en Railway Console")
        print("  3. Verifica que la IP esté permitida en Railway")
        print()
        
        return False
    
    finally:
        await engine.dispose()


async def quick_test():
    """Test rápido de conexión"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Conexión a base de datos: OK")
        return True
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    if "--quick" in sys.argv:
        asyncio.run(quick_test())
    else:
        asyncio.run(test_connection())
