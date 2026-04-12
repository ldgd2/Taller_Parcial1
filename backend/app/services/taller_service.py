"""
Servicio de Talleres — CU06 (Disponibilidad)
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.taller import Taller
from app.schemas.taller import DisponibilidadUpdate, TallerOut


async def obtener_taller(cod: str, db: AsyncSession) -> Taller:
    result = await db.execute(select(Taller).where(Taller.cod == cod))
    taller = result.scalar_one_or_none()
    if taller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado.",
        )
    return taller


async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    db: AsyncSession,
) -> TallerOut:
    """CU06 — El taller actualiza su estado operativo."""
    taller = await obtener_taller(cod, db)
    if data.estado not in ("ACTIVO", "INACTIVO"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado debe ser 'ACTIVO' o 'INACTIVO'.",
        )
    taller.estado = data.estado
    await db.flush()
    return TallerOut(
        cod=taller.cod,
        nombre=taller.nombre,
        direccion=taller.direccion,
        estado=taller.estado,
    )


async def listar_talleres_activos(db: AsyncSession):
    result = await db.execute(select(Taller).where(Taller.estado == "ACTIVO"))
    return result.scalars().all()
