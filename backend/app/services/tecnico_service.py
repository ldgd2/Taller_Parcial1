from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tecnico import Tecnico
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate, TecnicoOut
from app.core.security import hash_password

async def crear_tecnico(data: TecnicoCreate, db: AsyncSession) -> Tecnico:
    result = await db.execute(select(Tecnico).where(Tecnico.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Técnico ya registrado con este correo.",
        )
    
    tecnico = Tecnico(
        nombre=data.nombre,
        correo=data.correo,
        contrasena=hash_password(data.contrasena),
        telefono=data.telefono,
        idTaller=data.idTaller,
        estado="ACTIVO"
    )
    db.add(tecnico)
    await db.commit()
    await db.refresh(tecnico)
    return tecnico

async def obtener_tecnicos_taller(idTaller: str, db: AsyncSession):
    result = await db.execute(select(Tecnico).where(Tecnico.idTaller == idTaller))
    return result.scalars().all()

async def desactivar_tecnico(tecnico_id: int, db: AsyncSession):
    result = await db.execute(select(Tecnico).where(Tecnico.id == tecnico_id))
    tecnico = result.scalar_one_or_none()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    tecnico.estado = "INACTIVO"
    await db.commit()
    return tecnico
