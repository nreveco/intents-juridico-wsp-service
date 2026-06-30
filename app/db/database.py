import logging

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

logger = logging.getLogger(__name__)

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


async def _get_businesstype_enum_values(conn):
    result = await conn.scalars(text(
        "SELECT enumlabel FROM pg_enum "
        "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
        "WHERE pg_type.typname = 'businesstype' "
        "ORDER BY enumsortorder"
    ))
    return result.all()


async def init_db():
    """Crea todas las tablas si no existen."""
    from app.db import models  # noqa: F401 – needed so Base sees all models
    async with engine.begin() as conn:
        logger.info("Verificando enum 'businesstype' en la base de datos")
        exists = await conn.scalar(text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'businesstype')"
        ))

        if exists:
            values = await _get_businesstype_enum_values(conn)
            logger.info("Enum 'businesstype' actual: %s", values)
            if "law_firm" not in values:
                logger.info("Agregando valor 'law_firm' a enum 'businesstype'")
                await conn.execute(text(
                    "DO $$ BEGIN "
                    "IF NOT EXISTS (SELECT 1 FROM pg_enum "
                    "JOIN pg_type ON pg_enum.enumtypid = pg_type.oid "
                    "WHERE pg_type.typname = 'businesstype' AND enumlabel = 'law_firm') THEN "
                    "ALTER TYPE businesstype ADD VALUE 'law_firm'; "
                    "END IF; "
                    "END $$;"
                ))
        else:
            logger.info("Tipo enum 'businesstype' no existe; será creado durante create_all")

        await conn.run_sync(Base.metadata.create_all)

        exists_after = await conn.scalar(text(
            "SELECT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'businesstype')"
        ))
        if exists_after:
            values_after = await _get_businesstype_enum_values(conn)
            logger.info("Enum 'businesstype' después de init_db: %s", values_after)
        else:
            logger.warning("Después de create_all, el enum 'businesstype' sigue sin existir")
