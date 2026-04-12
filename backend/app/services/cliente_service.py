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
        vehiculos=[],  # Se carga la lista por separado si se necesita
    )


async def obtener_vehiculos_cliente(cliente_id: int, db: AsyncSession):
    result = await db.execute(
        select(Vehiculo).where(Vehiculo.idCliente == cliente_id)
    )
    return result.scalars().all()
