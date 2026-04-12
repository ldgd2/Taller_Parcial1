from sqlalchemy import Column, Integer, Numeric, Date, func
from app.core.database import Base


class Pago(Base):
    __tablename__ = "pago"

    id = Column(Integer, primary_key=True, index=True)
    monto = Column("Monto", Numeric(10, 2), nullable=False)
    monto_comision = Column("MontoComision", Numeric(10, 2), nullable=False)
    fecha_pago = Column("fechaPago", Date, nullable=False, server_default=func.current_date())
