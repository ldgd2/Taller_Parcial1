from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vehiculo import Vehiculo
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate

async def crear_vehiculo(data: VehiculoCreate, db: AsyncSession):
    vehiculo = Vehiculo(**data.model_dump())
    db.add(vehiculo)
    await db.commit()
    await db.refresh(vehiculo)
    return vehiculo

async def obtener_vehiculo(placa: str, db: AsyncSession):
    result = await db.execute(select(Vehiculo).where(Vehiculo.placa == placa))
    return result.scalar_one_or_none()

async def actualizar_vehiculo(placa: str, data: VehiculoUpdate, db: AsyncSession):
    vehiculo = await obtener_vehiculo(placa, db)
    if not vehiculo:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(vehiculo, key, value)
    await db.commit()
    await db.refresh(vehiculo)
    return vehiculo
