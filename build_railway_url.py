"""
Helper para construir la DATABASE_URL de Railway
"""
import sys

def build_railway_url():
    print("=" * 70)
    print("🔧 CONSTRUCTOR DE DATABASE_URL PARA RAILWAY")
    print("=" * 70)
    print()
    print("En Railway, ve a tu servicio PostgreSQL → Variables")
    print("Y copia los siguientes valores:")
    print()
    
    # Recopilar datos
    user = input("PGUSER (usualmente 'postgres'): ").strip() or "postgres"
    password = input("PGPASSWORD: ").strip()
    host = input("PGHOST (ej: reseau.proxy.rlwy.net): ").strip()
    port = input("PGPORT (ej: 13605): ").strip()
    database = input("PGDATABASE (usualmente 'railway'): ").strip() or "railway"
    
    if not password or not host or not port:
        print()
        print("❌ ERROR: Faltan datos requeridos")
        print("   PGPASSWORD, PGHOST y PGPORT son obligatorios")
        return None
    
    # Construir URL
    db_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"
    
    print()
    print("=" * 70)
    print("✅ DATABASE_URL CONSTRUIDA")
    print("=" * 70)
    print()
    print("Copia esto en tu archivo .env:")
    print()
    print(f"DATABASE_URL={db_url}")
    print()
    print("=" * 70)
    print()
    
    # Preguntar si quiere verificar
    test = input("¿Quieres verificar la conexión ahora? (s/n): ").strip().lower()
    
    if test == 's':
        print()
        print("Verificando conexión...")
        print()
        
        import os
        os.environ['DATABASE_URL'] = db_url
        
        # Recargar settings con nueva URL
        from importlib import reload
        from app import config
        reload(config)
        
        # Test de conexión
        import asyncio
        from sqlalchemy import text
        from app.db.database import engine
        
        async def quick_test():
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT version()"))
                    version = result.scalar()
                    print("✅ CONEXIÓN EXITOSA!")
                    print(f"   PostgreSQL: {version.split(',')[0]}")
                    print()
                    
                    # Contar tablas
                    result = await conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                    """))
                    count = result.scalar()
                    print(f"✅ Tablas encontradas: {count}")
                    
                    if count == 0:
                        print()
                        print("⚠️  No hay tablas. Ejecuta railway-init.sql en Railway")
                    
                    return True
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                print()
                print("Posibles causas:")
                print("  • Contraseña incorrecta")
                print("  • Host o puerto incorrectos")
                print("  • Base de datos no existe")
                print("  • Firewall bloqueando conexión")
                return False
            finally:
                await engine.dispose()
        
        success = asyncio.run(quick_test())
        
        if success:
            print()
            print("🎉 ¡Todo listo! Agrega la DATABASE_URL a tu .env")
        else:
            print()
            print("Verifica los datos y vuelve a intentar")
    
    return db_url


if __name__ == "__main__":
    print()
    print("Este script te ayuda a construir la DATABASE_URL de Railway")
    print("para conectarte desde tu entorno local.")
    print()
    
    url = build_railway_url()
    
    if url:
        print()
        print("Nota: Esta URL es para desarrollo local.")
        print("En Railway, usa: DATABASE_URL=${{Postgres.DATABASE_URL}}")
        print()
