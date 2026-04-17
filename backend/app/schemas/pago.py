from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

class PagoBase(BaseModel):
    monto: Decimal
    monto_comision: Decimal

class PagoCreate(PagoBase):
    pass

class PagoUpdate(PagoBase):
    monto: Optional[Decimal] = None
    monto_comision: Optional[Decimal] = None

class PagoOut(PagoBase):
    id: int
    fecha_pago: date

    class Config:
        from_attributes = True
