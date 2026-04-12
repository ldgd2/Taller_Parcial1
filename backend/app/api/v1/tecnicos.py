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
from app.schemas.taller import TecnicoOut

router = APIRouter(prefix="/tecnicos")


@router.get(
    "/perfil",
    response_model=TecnicoOut,
    summary="Perfil del técnico autenticado",
)
async def perfil(
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Tecnico).where(Tecnico.id == current["user_id"]))
    tecnico = result.scalar_one_or_none()
    return TecnicoOut(
        id=tecnico.id,
        nombre=tecnico.nombre,
        correo=tecnico.correo,
        telefono=tecnico.telefono,
        idTaller=tecnico.idTaller,
    )
