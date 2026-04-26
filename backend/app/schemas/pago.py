from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class PagoBase(BaseModel):
    monto: Decimal
    monto_comision: Decimal
    cliente_id: int
    emergencia_id: int

class PagoCreate(BaseModel):
    monto: Decimal
    emergencia_id: int

class PagoStripeCreate(BaseModel):
    emergencia_id: int
    metodo_pago_id: Optional[str] = None # Si es None, se asume que se añadirá una nueva tarjeta
    monto: Decimal

class PagoOut(PagoBase):
    id: int
    fecha_pago: date
    stripe_intent_id: Optional[str]
    estado: str
    metodo_pago_id: Optional[str]

    class Config:
        from_attributes = True
