"""
Servicio de Clientes — CU03
Registro de usuario y vehículo en una sola transacción.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.cliente import Cliente
from app.models.vehiculo import Vehiculo
from app.core.security import hash_password
from app.schemas.cliente import ClienteCreate, ClienteOut, ClienteSimpleCreate
from app.schemas.vehiculo import VehiculoCreate

async def registrar_cliente_solo(data: ClienteSimpleCreate, db: AsyncSession) -> ClienteOut:
    result = await db.execute(select(Cliente).where(Cliente.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado.",
        )
    cliente = Cliente(
        nombre=data.nombre,
        correo=data.correo,
        contrasena=hash_password(data.contrasena),
    )
    db.add(cliente)
    await db.flush()
    await db.refresh(cliente)

    return ClienteOut(
        id=cliente.id,
        nombre=cliente.nombre,
        correo=cliente.correo,
        vehiculos=[],
    )

async def registrar_cliente(data: ClienteCreate, db: AsyncSession) -> ClienteOut:
    cliente_simple = ClienteSimpleCreate(
        nombre=data.nombre,
        correo=data.correo,
        contrasena=data.contrasena
    )
    cliente_out = await registrar_cliente_solo(cliente_simple, db)

    vehiculo = Vehiculo(
        placa=data.vehiculo.placa,
        marca=data.vehiculo.marca,
        modelo=data.vehiculo.modelo,
        anio=data.vehiculo.anio,
        idCliente=cliente_out.id,
    )
    db.add(vehiculo)
    await db.flush()
    await db.refresh(vehiculo)

    cliente_out.vehiculos = [vehiculo]
    return cliente_out


async def registrar_vehiculo_extra(cliente_id: int, data: VehiculoCreate, db: AsyncSession):
    result = await db.execute(select(Vehiculo).where(Vehiculo.placa == data.placa))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La placa de vehículo ya se encuentra registrada en el sistema."
        )

    nuevo_vehiculo = Vehiculo(
        placa=data.placa,
        marca=data.marca,
        modelo=data.modelo,
        anio=data.anio,
        idCliente=cliente_id
    )
    db.add(nuevo_vehiculo)
    await db.flush()
    return nuevo_vehiculo




async def obtener_todos_los_clientes(db: AsyncSession):
    result = await db.execute(
        select(Cliente)
    )
    return result.scalars().all()


async def obtener_vehiculos_cliente(cliente_id: int, db: AsyncSession):
    result = await db.execute(
        select(Vehiculo).where(Vehiculo.idCliente == cliente_id)
    )
    return result.scalars().all()
