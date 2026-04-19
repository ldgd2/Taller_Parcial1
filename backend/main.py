"""
Plataforma Inteligente de Atención de Emergencias Vehiculares
Backend FastAPI — Punto de entrada principal

Arquitectura de paquetes (Ciclo 3):
  ┌─────────────────────────────────────────────────────────────────┐
  │  PAQUETE                  │  CASOS DE USO                       │
  ├───────────────────────────┼─────────────────────────────────────┤
  │  perfil_seguridad         │  CU01 CU02 CU03 CU06 CU07 CU13     │
  │  gestion_ia               │  CU04 CU08 CU09 CU10 CU11 CU12     │
  │  gestion_comercio         │  CU05 CU14 CU15                     │
  └───────────────────────────┴─────────────────────────────────────┘
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine, Base

# ─── Importar todos los modelos para que Alembic los detecte ──────
from app.models import *  # noqa: F401, F403

# ─── Paquetes de la nueva arquitectura ────────────────────────────
from app.api.v1.perfil_seguridad import router as perfil_seguridad_router
from app.api.v1.gestion_ia import router as gestion_ia_router
from app.api.v1.gestion_comercio import router as gestion_comercio_router

# Catálogos (transversal — especialidades, prioridades, categorías)
from app.api.v1.catalogos import router as catalogos_router

app = FastAPI(
    title=settings.APP_NAME,
    version="3.0.0",
    description="""
## Plataforma de Emergencias Vehiculares — Ciclo 3

### Arquitectura de Paquetes

| Paquete | Responsabilidad | CUs |
|---|---|---|
| **Gestión Perfil y Seguridad** | Autenticación, roles y disponibilidad operativa | CU01–CU03, CU06–CU07, CU13 |
| **Gestión IA** | Clasificación, priorización, ficha técnica y motor de asignación | CU04, CU08–CU12 |
| **Gestión Comercio** | Solicitudes, historial e transacciones financieras | CU05, CU14–CU15 |
    """,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── Configuración Almacenamiento Multimedia (Storage) ────────────
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


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

# ─── Registrar paquetes ───────────────────────────────────────────
PREFIX = settings.API_V1_PREFIX

# Paquete 1: Gestión Perfil y Seguridad (CU01/CU02/CU03/CU06/CU07/CU13)
app.include_router(perfil_seguridad_router, prefix=PREFIX)

# Paquete 2: Gestión IA (CU04/CU08/CU09/CU10/CU11/CU12)
app.include_router(gestion_ia_router, prefix=PREFIX)

# Paquete 3: Gestión Comercio (CU05/CU14/CU15)
app.include_router(gestion_comercio_router, prefix=PREFIX)

# Catálogos (transversal — especialidades, prioridades, categorías)
app.include_router(catalogos_router, prefix=PREFIX)


@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "version": "3.0.0",
        "paquetes": ["perfil_seguridad", "gestion_ia", "gestion_comercio"],
        "message": "Plataforma de Emergencias Vehiculares operativa."
    }
