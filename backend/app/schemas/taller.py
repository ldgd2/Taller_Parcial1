from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ─── Taller ───────────────────────────────────────────────────────

class TallerOut(BaseModel):
    cod: str
    nombre: str
    direccion: str
    estado: str

    model_config = {"from_attributes": True}


# ─── Técnico ──────────────────────────────────────────────────────

class TecnicoCreate(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    telefono: str


class TecnicoOut(BaseModel):
    id: int
    nombre: str
    correo: str
    telefono: str
    idTaller: str

    model_config = {"from_attributes": True}


# ─── Disponibilidad (CU06) ────────────────────────────────────────

class DisponibilidadUpdate(BaseModel):
    estado: str  # "ACTIVO" | "INACTIVO"
