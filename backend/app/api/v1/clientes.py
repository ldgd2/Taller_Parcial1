"""
Router de Clientes — CU03
POST /clientes/registro → Registro de usuario + vehículo
GET  /clientes/mis-vehiculos → Listar vehículos del cliente autenticado
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.schemas.cliente import ClienteCreate, ClienteOut, VehiculoOut
from app.services import cliente_service

router = APIRouter(prefix="/clientes")


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
    summary="Listar mis vehículos",
)
async def mis_vehiculos(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    vehiculos = await cliente_service.obtener_vehiculos_cliente(current["user_id"], db)
    return vehiculos
