from sqlalchemy import Column, Integer, String, Text, Date, Time, ForeignKey, func, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class Emergencia(Base):
    __tablename__ = "emergencia"

    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String(500), nullable=False)
    texto_adicional = Column("textoAdicional", Text, nullable=True)
    direccion = Column(String(500), nullable=False)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    fecha = Column(Date, nullable=False, server_default=func.current_date())
    hora = Column(Time, nullable=False)

    # Claves foráneas
    idTaller = Column(String(10), ForeignKey("taller.cod"), nullable=False, index=True)
    idPrioridad = Column(Integer, ForeignKey("prioridad.id"), nullable=False)
    idCategoria = Column(Integer, ForeignKey("categoria_problema.id"), nullable=False)
    idCliente = Column(Integer, ForeignKey("cliente.id"), nullable=False, index=True)
    placaVehiculo = Column(String(20), ForeignKey("vehiculo.placa"), nullable=False, index=True)
    idPago = Column(Integer, ForeignKey("pago.id"), nullable=True)

    # Relaciones
    taller = relationship("Taller", back_populates="emergencias")
    prioridad = relationship("Prioridad")
    categoria = relationship("CategoriaProblema")
    cliente = relationship("Cliente", back_populates="emergencias")
    vehiculo = relationship("Vehiculo", back_populates="emergencias")
    pago = relationship("Pago")
    evidencias = relationship("Evidencia", back_populates="emergencia")
    historial = relationship("HistorialEstado", back_populates="emergencia")
    resumen_ia = relationship("ResumenIA", back_populates="emergencia", uselist=False)
