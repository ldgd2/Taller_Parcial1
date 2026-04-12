from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Tecnico(Base):
    __tablename__ = "tecnico"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    correo = Column(String(255), nullable=False, unique=True, index=True)
    contrasena = Column("contraseña", String(255), nullable=False)
    telefono = Column(String(20), nullable=False)
    idTaller = Column(String(10), ForeignKey("taller.cod"), nullable=False, index=True)

    # Relaciones
    taller = relationship("Taller", back_populates="tecnicos")
    asignaciones = relationship("AsignacionEspecialidad", back_populates="tecnico")
