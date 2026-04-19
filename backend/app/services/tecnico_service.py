from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tecnico import Tecnico
from app.schemas.tecnico import TecnicoCreate, TecnicoUpdate, TecnicoOut
from app.core.security import hash_password
from sqlalchemy.orm import selectinload

from sqlalchemy.exc import IntegrityError

async def crear_tecnico(data: TecnicoCreate, db: AsyncSession) -> Tecnico:
    result = await db.execute(select(Tecnico).where(Tecnico.correo == data.correo))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Técnico ya registrado con este correo.",
        )
    
    try:
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
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fallo de integridad: El taller {data.idTaller} no existe o no tiene perfil activo."
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    # Re-recuperar con especialidades para serialización async
    stmt = select(Tecnico).options(selectinload(Tecnico.especialidades)).where(Tecnico.id == tecnico.id)
    res = await db.execute(stmt)
    return res.scalar_one()

async def obtener_tecnico_by_id(tecnico_id: int, db: AsyncSession) -> Tecnico:
    stmt = select(Tecnico).options(selectinload(Tecnico.especialidades)).where(Tecnico.id == tecnico_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

async def obtener_tecnicos_taller(idTaller: str, db: AsyncSession):
    stmt = select(Tecnico).options(selectinload(Tecnico.especialidades)).where(Tecnico.idTaller == idTaller)
    result = await db.execute(stmt)
    return result.scalars().all()

async def actualizar_tecnico(tecnico_id: int, data: TecnicoUpdate, db: AsyncSession) -> Tecnico:
    tecnico = await obtener_tecnico_by_id(tecnico_id, db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    if data.nombre is not None: tecnico.nombre = data.nombre
    if data.correo is not None: tecnico.correo = data.correo
    if data.telefono is not None: tecnico.telefono = data.telefono
    if data.contrasena is not None: tecnico.contrasena = hash_password(data.contrasena)
    if data.estado is not None: tecnico.estado = data.estado
    
    await db.commit()
    return await obtener_tecnico_by_id(tecnico_id, db)

async def desactivar_tecnico(tecnico_id: int, db: AsyncSession):
    result = await db.execute(select(Tecnico).where(Tecnico.id == tecnico_id))
    tecnico = result.scalar_one_or_none()
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    tecnico.estado = "INACTIVO"
    await db.commit()
    return tecnico


async def actualizar_especialidades_tecnico(tecnico_id: int, especialidades_ids: list, db: AsyncSession) -> Tecnico:
    """CU13 — Gestionar Rol: asigna/reemplaza especialidades del técnico."""
    from sqlalchemy import delete
    from app.models.tecnico_especialidad import TecnicoEspecialidad
    
    tecnico = await obtener_tecnico_by_id(tecnico_id, db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico no encontrado")
    
    # 1. Eliminar asignaciones actuales
    await db.execute(
        delete(TecnicoEspecialidad).where(TecnicoEspecialidad.idTecnico == tecnico_id)
    )
    # 2. Insertar nuevas
    for esp_id in especialidades_ids:
        db.add(TecnicoEspecialidad(idTecnico=tecnico_id, idEspecialidad=esp_id))
    
    await db.commit()
    return await obtener_tecnico_by_id(tecnico_id, db)
