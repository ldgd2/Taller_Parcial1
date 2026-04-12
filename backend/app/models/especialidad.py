from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Especialidad(Base):
    __tablename__ = "especialidad"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
