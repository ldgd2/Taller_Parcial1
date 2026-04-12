"""
Router de Talleres — CU06 / CU15
PATCH /talleres/{cod}/disponibilidad → CU06 Gestión de disponibilidad
GET   /talleres/{cod}/solicitudes    → CU15 Ver solicitudes del taller
PATCH /talleres/solicitudes/{id}/estado → CU15 Actualizar estado
GET   /talleres/activos              → Listar talleres activos (público)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.schemas.taller import TallerOut, DisponibilidadUpdate
from app.schemas.emergencia import EmergenciaOut, ActualizarEstadoRequest
from app.services import taller_service, emergencia_service

router = APIRouter(prefix="/talleres")


@router.get(
    "/activos",
    response_model=List[TallerOut],
    summary="Listar talleres activos",
)
async def talleres_activos(db: AsyncSession = Depends(get_db)):
    return await taller_service.listar_talleres_activos(db)


@router.patch(
    "/{cod}/disponibilidad",
    response_model=TallerOut,
    summary="CU06 — Gestión de disponibilidad del taller",
)
async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    """Solo técnicos autenticados del taller pueden cambiar su estado."""
    return await taller_service.actualizar_disponibilidad(cod, data, db)


@router.get(
    "/{cod}/solicitudes",
    response_model=List[EmergenciaOut],
    summary="CU15 — Ver solicitudes asignadas al taller",
)
async def solicitudes_taller(
    cod: str,
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    return await emergencia_service.listar_emergencias_taller(cod, db)


@router.patch(
    "/solicitudes/{emergencia_id}/estado",
    summary="CU15 — Actualizar estado de una emergencia",
)
async def actualizar_estado(
    emergencia_id: int,
    data: ActualizarEstadoRequest,
    current=Depends(require_role("tecnico")),
    db: AsyncSession = Depends(get_db),
):
    # El taller del técnico viene en el JWT payload
    # Por ahora lo obtenemos del token; en iter. futuras del perfil BD
    taller_cod = current.get("taller")
    historial = await emergencia_service.actualizar_estado_emergencia(
        emergencia_id, data, taller_cod, db
    )
    return {"message": "Estado actualizado", "historial_id": historial.id}
