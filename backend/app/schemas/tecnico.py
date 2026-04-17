from pydantic import BaseModel, EmailStr
from typing import Optional

class TecnicoBase(BaseModel):
    nombre: str
    correo: EmailStr
    telefono: str
    idTaller: str

class TecnicoCreate(TecnicoBase):
    contrasena: str

class TecnicoUpdate(BaseModel):
    nombre: Optional[str] = None
    correo: Optional[EmailStr] = None
    contrasena: Optional[str] = None
    telefono: Optional[str] = None
    idTaller: Optional[str] = None
    estado: Optional[str] = None

class TecnicoOut(TecnicoBase):
    id: int
    estado: str

    class Config:
        from_attributes = True
