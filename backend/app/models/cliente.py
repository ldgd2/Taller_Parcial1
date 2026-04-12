from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)

    # Relaciones
    vehiculos = relationship("Vehiculo", back_populates="cliente")
    emergencias = relationship("Emergencia", back_populates="cliente")
