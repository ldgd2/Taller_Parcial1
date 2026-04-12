from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class AsignacionEspecialidad(Base):
    __tablename__ = "asignacion_especialidad"

    idTecnico = Column(Integer, ForeignKey("tecnico.id"), primary_key=True)
    idEspecialidad = Column(Integer, ForeignKey("especialidad.id"), primary_key=True)

    # Relaciones
    tecnico = relationship("Tecnico", back_populates="asignaciones")
    especialidad = relationship("Especialidad")
