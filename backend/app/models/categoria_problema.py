from sqlalchemy import Column, Integer, String
from app.core.database import Base


class CategoriaProblema(Base):
    __tablename__ = "categoria_problema"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String(255), nullable=False)
