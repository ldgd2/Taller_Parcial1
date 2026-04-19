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
from pydantic import BaseModel
from sqlalchemy import select
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from app.models.prioridad import Prioridad
from app.models.categoria_problema import CategoriaProblema
from app.schemas.ai_schemas import AnalisisEstructuradoIA
from app.services.ai_service import analizar_transcripcion_whisper
from app.services.transcripcion_service import transcribir_audio_local

class TextoAudioRequest(BaseModel):
    texto_crudo: str

router = APIRouter(prefix="/emergencias")

@router.post(
    "/analizar-audio",
    response_model=AnalisisEstructuradoIA,
    summary="CU08, CU09, CU10 — Pre-Analizar AUDIO Whisper con IA",
)
async def analizar_audio_ia(
    archivo_audio: UploadFile = File(..., description="Archivo de audio grabado por el usuario en formato común (mp3, wav, m4a)"),
    current=Depends(require_role("cliente")),
    db: AsyncSession = Depends(get_db),
):
    """
    Recibe el archivo de audio subido, lo pasa por Whisper Local para obtener 
    la transcripción, y luego lo clasifica con OpenRouter. Útil para que el cliente confirme.
    """
    try:
        # 1. Transcribir el audio usando modelo local (faster-whisper)
        texto_crudo = await transcribir_audio_local(archivo_audio)
        
        # 2. IA Classification / Extraction
        cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.descripcion))
        prios_res = await db.execute(select(Prioridad.id, Prioridad.descripcion))
        categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in cats_res.all()]
        prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prios_res.all()]
        
        resultado = await analizar_transcripcion_whisper(
            texto_crudo=texto_crudo,
            categorias_disponibles=categorias_activas,
            prioridades_disponibles=prioridades_activas
        )
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en procesamiento: {str(e)}")


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
    return await emergencia_service.listar_emergencias_cliente(
        current["user_id"], db
    )
