from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ─── Vehículo ─────────────────────────────────────────────────────

class VehiculoCreate(BaseModel):
    placa: str
    marca: str
    modelo: str
    anio: int

    model_config = {"from_attributes": True}


class VehiculoOut(VehiculoCreate):
    id: int
    idCliente: int


# ─── Cliente ──────────────────────────────────────────────────────

class ClienteCreate(BaseModel):
    nombre: str
    correo: EmailStr
    contrasena: str
    vehiculo: VehiculoCreate     # CU03: registro simultáneo vehículo


class ClienteOut(BaseModel):
    id: int
    nombre: str
    correo: str
    vehiculos: List[VehiculoOut] = []

    model_config = {"from_attributes": True}
