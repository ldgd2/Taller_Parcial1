"""
Router de Emergencias — CU04 / CU14
POST /emergencias/reportar          → CU04 Reportar emergencia
GET  /emergencias/mis-solicitudes   → CU14 Ver solicitudes del cliente
"""
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import datetime

from app.core.database import get_db
from app.core.dependencies import require_role
from app.schemas.emergencia import EmergenciaCreate, EmergenciaOut
from app.services import emergencia_service

router = APIRouter(prefix="/emergencias")


@router.post(
    "/reportar",
    response_model=EmergenciaOut,
    status_code=201,
    summary="CU04 — Reportar emergencia vehicular",
)
async def reportar(
    data: EmergenciaCreate,
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    El cliente envía los datos de la emergencia.
    El motor de asignación (CU11) selecciona automáticamente el taller.
    """
    return await emergencia_service.reportar_emergencia(data, current["user_id"], db)


@router.get(
    "/mis-solicitudes",
    response_model=List[EmergenciaOut],
    summary="CU14 — Ver mis solicitudes de auxilio",
)
async def mis_solicitudes(
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    emergencias = await emergencia_service.listar_emergencias_cliente(
        current["user_id"], db
    )
    return [
        EmergenciaOut(
            id=e.id,
            descripcion=e.descripcion,
            texto_adicional=e.texto_adicional,
            ubicacion=e.ubicacion,
            fecha=e.fecha,
            hora=e.hora,
            idTaller=e.idTaller,
            idPrioridad=e.idPrioridad,
            idCategoria=e.idCategoria,
        )
        for e in emergencias
    ]
