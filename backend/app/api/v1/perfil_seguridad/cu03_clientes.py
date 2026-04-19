"""
CU03 — Registro de Usuario y Vehículo

POST /clientes/registro      → Crear cuenta de cliente + primer vehículo
GET  /clientes/mis-vehiculos → Listar vehículos del cliente autenticado
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import require_role
from app.schemas.cliente import ClienteCreate, ClienteOut, VehiculoOut
from app.services import cliente_service

router = APIRouter(prefix="/clientes", tags=["GPS — Clientes (CU03)"])


@router.post(
    "/registro",
    response_model=ClienteOut,
    status_code=201,
    summary="CU03 — Registro de usuario y vehículo",
)
async def registrar(data: ClienteCreate, db: AsyncSession = Depends(get_db)):
    """Crea la cuenta del cliente y registra su primer vehículo."""
    return await cliente_service.registrar_cliente(data, db)


@router.get(
    "/mis-vehiculos",
    response_model=List[VehiculoOut],
    summary="CU03 — Listar mis vehículos",
)
async def mis_vehiculos(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    return await cliente_service.obtener_vehiculos_cliente(current["user_id"], db)


@router.post(
    "/vehiculos",
    response_model=VehiculoOut,
    status_code=201,
    summary="CU03 — Registrar un nuevo vehículo para la cuenta",
)
async def registrar_nuevo_vehiculo(
    data: VehiculoCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """Permite al cliente agregar 2do o 3er autos a su garaje para emergencias."""
    nuevo_auto = await cliente_service.registrar_vehiculo_extra(current["user_id"], data, db)
    await db.commit() # Salvamos este auto (El CU01 usa flush y el autocommit del worker route)
    await db.refresh(nuevo_auto)
    return nuevo_auto
