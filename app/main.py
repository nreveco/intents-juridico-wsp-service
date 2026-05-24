from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
from app.routers import webhook, admin
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando — creando tablas en base de datos...")
    await init_db()
    logger.info("Base de datos lista ✓")
    yield
    logger.info("Apagando servidor")


app = FastAPI(
    title="WhatsApp AI Automation Engine",
    description="Motor de automatización WhatsApp + IA para PyMEs — restaurantes, talleres, clínicas y más.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
async def root():
    return {
        "service": "WhatsApp AI Automation Engine",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}
