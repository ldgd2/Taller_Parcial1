from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.evidencia import Evidencia
from app.models.historial_estado import HistorialEstado
from app.schemas.transacciones import EvidenciaCreate, HistorialEstadoCreate

async def registrar_evidencia(data: EvidenciaCreate, db: AsyncSession):
    evidencia = Evidencia(**data.model_dump())
    db.add(evidencia)
    await db.commit()
    await db.refresh(evidencia)
    return evidencia

async def registrar_cambio_estado(data: HistorialEstadoCreate, db: AsyncSession):
    historial = HistorialEstado(**data.model_dump())
    db.add(historial)
    await db.commit()
    await db.refresh(historial)
    return historial

async def obtener_historial_emergencia(idEmergencia: int, db: AsyncSession):
    res = await db.execute(select(HistorialEstado).where(HistorialEstado.idEmergencia == idEmergencia))
    return res.scalars().all()

async def obtener_evidencias_emergencia(idEmergencia: int, db: AsyncSession):
    res = await db.execute(select(Evidencia).where(Evidencia.idEmergencia == idEmergencia))
    return res.scalars().all()
