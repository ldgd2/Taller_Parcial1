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
from app.schemas.cliente import ClienteCreate, ClienteOut


async def registrar_cliente(data: ClienteCreate, db: AsyncSession) -> ClienteOut:
    # Verificar correo único
    result = await db.execute(select(Cliente).where(Cliente.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo electrónico ya está registrado.",
        )

    # Crear cliente
    cliente = Cliente(
        nombre=data.nombre,
        correo=data.correo,
        contrasena=hash_password(data.contrasena),
    )
    db.add(cliente)
    await db.flush()  # obtener el id sin hacer commit

    # Crear vehículo vinculado
    vehiculo = Vehiculo(
        placa=data.vehiculo.placa,
        marca=data.vehiculo.marca,
        modelo=data.vehiculo.modelo,
        anio=data.vehiculo.anio,
        idCliente=cliente.id,
    )
    db.add(vehiculo)
    await db.flush()

    await db.refresh(cliente)
    await db.refresh(vehiculo)

    return ClienteOut(
        id=cliente.id,
        nombre=cliente.nombre,
        correo=cliente.correo,
        vehiculos=[vehiculo],  # Devolvemos el vehículo ahora que tenemos la placa
    )


async def registrar_vehiculo_extra(cliente_id: int, data: VehiculoCreate, db: AsyncSession):
    # Verificamos si la placa ya existe
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
    # Commit delegamos pero podemos hacer flush para validarlo
    await db.flush()
    return nuevo_vehiculo




async def obtener_vehiculos_cliente(cliente_id: int, db: AsyncSession):
    result = await db.execute(
        select(Vehiculo).where(Vehiculo.idCliente == cliente_id)
    )
    return result.scalars().all()
