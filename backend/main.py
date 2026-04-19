"""
Plataforma Inteligente de Atención de Emergencias Vehiculares
Backend FastAPI — Punto de entrada principal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base

# ─── Importar todos los modelos para que Alembic los detecte ──────
from app.models import *  # noqa: F401, F403

# ─── Routers ──────────────────────────────────────────────────────
from app.api.v1 import auth, clientes, talleres, emergencias, tecnicos, emergencias_admin, catalogos, pagos

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API REST para la gestión de emergencias vehiculares — Ciclo 3",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200", 
        "http://127.0.0.1:4200"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Registrar routers ────────────────────────────────────────────
PREFIX = settings.API_V1_PREFIX

app.include_router(auth.router,        prefix=PREFIX, tags=["Autenticación"])
app.include_router(clientes.router,    prefix=PREFIX, tags=["Clientes"])
app.include_router(talleres.router,    prefix=PREFIX, tags=["Talleres"])
app.include_router(emergencias.router, prefix=PREFIX, tags=["Emergencias"])
app.include_router(emergencias_admin.router, prefix=f"{PREFIX}/gestion-emergencia", tags=["Gestión Emergencia"])
app.include_router(tecnicos.router,    prefix=PREFIX, tags=["Técnicos"])
app.include_router(catalogos.router,   prefix=PREFIX, tags=["Catálogos"])
app.include_router(pagos.router,       prefix=PREFIX, tags=["Pagos"])


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "API funcionando correctamente"}
