from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.pago import Pago
from app.schemas.pago import PagoCreate

async def registrar_pago(data: PagoCreate, db: AsyncSession):
    pago = Pago(**data.model_dump())
    db.add(pago)
    await db.commit()
    await db.refresh(pago)
    return pago

async def obtener_pagos_emergencia(db: AsyncSession):
    # En este diseño el pago está vinculado a la emergencia por id
    result = await db.execute(select(Pago))
    return result.scalars().all()
