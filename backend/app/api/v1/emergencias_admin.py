from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.services import emergencia_service
from app.schemas.emergencia import EmergenciaOut, ActualizarEstadoRequest

router = APIRouter()

@router.get("/disponibles", response_model=List[EmergenciaOut])
async def listar_emergencias_disponibles(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    # El taller_cod viene en el token para administradores de taller
    taller_cod = current_user.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=400, detail="El usuario no tiene un taller asociado.")
        
    return await emergencia_service.listar_emergencias_disponibles(taller_cod, db)

@router.get("/asignadas", response_model=List[EmergenciaOut])
async def listar_emergencias_asignadas(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    taller_cod = current_user.get("taller")
    if not taller_cod:
        raise HTTPException(status_code=400, detail="El usuario no tiene un taller asociado.")
        
    return await emergencia_service.listar_emergencias_taller(taller_cod, db)
@router.get("/{id}", response_model=EmergenciaOut)
async def obtener_emergencia(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    """Obtiene el detalle completo de una emergencia específica."""
    emergencia = await emergencia_service.obtener_emergencia_detalle(id, db)
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    return emergencia

@router.post("/{id}/analizar")
async def bloquear_emergencia(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.bloquear_emergencia_temporal(id, taller_cod, db)



from pydantic import BaseModel

class AsignarTecnicosRequest(BaseModel):
    tecnicos_ids: List[int]

@router.post("/{id}/asignar")
async def confirmar_asignacion(
    id: int,
    data: AsignarTecnicosRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.asignar_emergencia_taller(id, taller_cod, data.tecnicos_ids, db)

@router.post("/{id}/estado")
async def actualizar_estado_tecnico(
    id: int,
    data: ActualizarEstadoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    taller_cod = current_user.get("taller")
    return await emergencia_service.actualizar_estado_emergencia(id, data, taller_cod, db)
