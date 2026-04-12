from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Vehiculo(Base):
    __tablename__ = "vehiculo"

    id = Column(Integer, primary_key=True, index=True)
    marca = Column(String(100), nullable=False)
    modelo = Column(String(100), nullable=False)
    anio = Column("año", Integer, nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.id"), nullable=False, index=True)

    # Relaciones
    cliente = relationship("Cliente", back_populates="vehiculos")
    emergencias = relationship("Emergencia", back_populates="vehiculo")
