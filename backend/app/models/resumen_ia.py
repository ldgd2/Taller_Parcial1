from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class ResumenIA(Base):
    __tablename__ = "resumen_ia"

    id = Column(Integer, primary_key=True)
    resumen = Column("Resumen", Text, nullable=False)
    idEmergencia = Column(Integer, ForeignKey("emergencia.id"), nullable=False, index=True)

    emergencia = relationship("Emergencia", back_populates="resumen_ia")
