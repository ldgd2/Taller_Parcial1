from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime


# ─── Crear emergencia ─────────────────────────────────────────────

class EmergenciaCreate(BaseModel):
    descripcion: str
    texto_adicional: Optional[str] = None
    ubicacion: str
    hora: time
    idVehiculo: int
    # idTaller, idPrioridad, idCategoria son asignados por el motor de asignación


# ─── Respuesta emergencia ─────────────────────────────────────────

class EmergenciaOut(BaseModel):
    id: int
    descripcion: str
    texto_adicional: Optional[str]
    ubicacion: str
    fecha: date
    hora: time
    idTaller: str
    idPrioridad: int
    idCategoria: int
    estado_actual: Optional[str] = None   # Calculado desde historial

    model_config = {"from_attributes": True}


# ─── Actualizar estado (CU15 — Taller) ───────────────────────────

class ActualizarEstadoRequest(BaseModel):
    idEstado: int
    comentario: Optional[str] = None


# ─── Evidencia ────────────────────────────────────────────────────

class EvidenciaOut(BaseModel):
    id: int
    direccion: str
    idEmergencia: int

    model_config = {"from_attributes": True}
