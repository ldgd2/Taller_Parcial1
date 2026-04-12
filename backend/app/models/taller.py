from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Taller(Base):
    __tablename__ = "taller"

    cod = Column(String(10), primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    direccion = Column(String(500), nullable=False)
    estado = Column(String(20), nullable=False, default="ACTIVO")

    # Relaciones
    tecnicos = relationship("Tecnico", back_populates="taller")
    emergencias = relationship("Emergencia", back_populates="taller")
