from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

# Asegurar que la URL use asyncpg
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not db_url.startswith("postgresql+asyncpg://"):
    raise ValueError(f"DATABASE_URL debe usar postgresql+asyncpg:// (actual: {db_url[:30]}...)")

engine = create_async_engine(
    db_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Crea todas las tablas si no existen."""
    from app.db import models  # noqa: F401 – needed so Base sees all models
    async with engine.begin() as conn:
        # Actualiza el enum `businesstype` en la base de datos existente.
        # Esto evita LookupError cuando el enum se creó con valores antiguos.
        await conn.execute(text(
            "ALTER TYPE businesstype ADD VALUE IF NOT EXISTS 'law_firm';"
        ))
        await conn.run_sync(Base.metadata.create_all)
