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
    es_valida: bool = Field(description="Determina si el reporte es una emergencia mecánica real de un vehículo.")
    motivo_rechazo: str = Field(description="Si es_valida es falso, explica por qué (ej: broma, fuera de contexto, código python, etc).")
    recomendaciones_taller: str = Field(description="Recomendaciones estratégicas para el taller sobre cómo abordar este cliente o este problema específico.")

class ItemCosto(BaseModel):
    item: str = Field(description="Nombre del servicio o repuesto.")
    costo: float = Field(description="Costo estimado en USD o moneda local.")

class SimulacionCostoIA(BaseModel):
    mano_de_obra: float = Field(description="Costo base del servicio mecánico.")
    repuestos_estimados: List[ItemCosto] = Field(description="Lista de posibles repuestos necesarios con sus costos.")
    comision_sistema: float = Field(description="10% de ganancia para la plataforma.")
    total_estimado: float = Field(description="Suma total de todos los rubros.")
    justificacion_mercado: str = Field(description="Explicación de por qué se cobra ese monto basado en precios de mercado y tipo de falla.")
