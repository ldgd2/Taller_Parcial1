from pydantic import BaseModel, Field
from typing import List

class FichaTecnica(BaseModel):
    diagnostico_probable: str = Field(description="Deducción técnica del problema basada en los síntomas.")
    piezas_necesarias: List[str] = Field(description="Componentes internos del vehículo que podrían estar fallando.")
    repuestos_sugeridos: List[str] = Field(description="Lista de repuestos específicos que el taller debe llevar.")
    protocolo_tecnico: List[str] = Field(description="Pasos críticos para el técnico antes y durante la intervención.")

class AnalisisEstructuradoIA(BaseModel):
    titulo_emergencia: str = Field(description="Título corto, descriptivo y profesional del problema (Máx 60 caracteres).")
    resumen_taller: str = Field(description="Resumen técnico EXCLUSIVO para el taller (no para el cliente).")
    id_categoria: int = Field(description="ID de la categoría de problema.")
    id_prioridad: int = Field(description="ID de la prioridad asignada.")
    ficha_tecnica: FichaTecnica = Field(description="Ficha técnica detallada para el mecánico.")
