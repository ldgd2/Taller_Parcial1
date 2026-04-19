"""
Router de Técnicos — CU07 (base Ciclo 2, esqueleto en Ciclo 1)
GET /tecnicos/perfil → Datos del técnico autenticado
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.tecnico import Tecnico
from app.models.tecnico_especialidad import TecnicoEspecialidad
from app.schemas.tecnico import TecnicoOut, TecnicoCreate, TecnicoUpdate
from app.services import tecnico_service
from typing import List

router = APIRouter(prefix="/tecnicos")


@router.post(
    "/",
    response_model=TecnicoOut,
    summary="Registrar un nuevo técnico (Admin)",
)
async def crear_tecnico(
    data: TecnicoCreate,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await tecnico_service.crear_tecnico(data, db)


@router.put(
    "/{tecnico_id}",
    response_model=TecnicoOut,
    summary="Actualizar un técnico",
)
async def actualizar_tecnico(
    tecnico_id: int,
    data: TecnicoUpdate,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await tecnico_service.actualizar_tecnico(tecnico_id, data, db)


@router.delete(
    "/{tecnico_id}",
    summary="Desactivar un técnico",
)
async def desactivar_tecnico(
    tecnico_id: int,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    await tecnico_service.desactivar_tecnico(tecnico_id, db)
    return {"status": "ok", "message": "Técnico desactivado"}


@router.get(
    "/taller/{idTaller}",
    response_model=List[TecnicoOut],
    summary="Listar técnicos de un taller",
)
async def listar_tecnicos_taller(
    idTaller: str,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    return await tecnico_service.obtener_tecnicos_taller(idTaller, db)


@router.get(
    "/perfil",
    response_model=TecnicoOut,
    summary="Perfil del técnico autenticado",
)
async def perfil(
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    tecnico = await tecnico_service.obtener_tecnico_by_id(current["user_id"], db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    return tecnico


@router.put(
    "/{tecnico_id}/especialidades",
    response_model=TecnicoOut,
    summary="CU13 — Asignar especialidades a un técnico (Gestionar Rol)",
)
async def asignar_especialidades_tecnico(
    tecnico_id: int,
    especialidades_ids: List[int],
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU13: Gestionar Rol — Asigna las especialidades (rol técnico) al perfil del técnico.
    Reemplaza las especialidades actuales con las nuevas.
    """
    return await tecnico_service.actualizar_especialidades_tecnico(tecnico_id, especialidades_ids, db)
