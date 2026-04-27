"""
Servicio de Talleres — CU06 (Disponibilidad)
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.models.taller import Taller
from app.schemas.taller import DisponibilidadUpdate, TallerOut, TallerCreate, TallerUpdate
import re
import random
import string
from sqlalchemy.orm import joinedload
from app.models.asignacion_especialidad import AsignacionEspecialidad


def generate_workshop_code(name: str) -> str:
    """Genera un código de 10 caracteres basado en el nombre + 4 caracteres aleatorios."""
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    base = clean_name[:6]
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    code = base.ljust(6, 'X')[:6] + random_suffix
    return code


async def obtener_taller_por_codigo(cod: str, db: AsyncSession) -> Taller:
    stmt = (
        select(Taller)
        .options(joinedload(Taller.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
        .where(Taller.cod == cod)
    )
    result = await db.execute(stmt)
    taller = result.unique().scalar_one_or_none()
    if taller:
        taller.especialidades = [a.especialidad for a in taller.asignaciones]
    if taller is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Taller no encontrado.",
        )
    return taller


async def actualizar_especialidades_taller(cod: str, especialidades_ids: List[int], db: AsyncSession):
    taller = await obtener_taller_por_codigo(cod, db)
    
    from sqlalchemy import delete
    # 1. Eliminar actuales
    await db.execute(
        delete(AsignacionEspecialidad).where(AsignacionEspecialidad.idTaller == cod)
    )
    # 2. Insertar nuevas
    for e_id in especialidades_ids:
        db.add(AsignacionEspecialidad(idTaller=cod, idEspecialidad=e_id))
    
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


async def crear_taller(data: TallerCreate, admin_id: int, db: AsyncSession) -> Taller:
    workshop_cod = generate_workshop_code(data.nombre)
    taller = Taller(
        cod=workshop_cod,
        nombre=data.nombre,
        direccion=data.direccion,
        latitud=data.latitud,
        longitud=data.longitud,
        estado="ACTIVO",
        id_admin=admin_id
    )
    db.add(taller)
    await db.commit()
    await db.refresh(taller)
    return taller


async def listar_talleres_admin(admin_id: int, db: AsyncSession):
    stmt = (
        select(Taller)
        .options(joinedload(Taller.asignaciones).joinedload(AsignacionEspecialidad.especialidad))
        .where(Taller.id_admin == admin_id)
    )
    result = await db.execute(stmt)
    talleres = result.scalars().unique().all()
    # Transformar para el schema
    for t in talleres:
        t.especialidades = [a.especialidad for a in t.asignaciones]
    return talleres


async def actualizar_taller(cod: str, data: TallerUpdate, db: AsyncSession) -> Taller:
    taller = await obtener_taller_por_codigo(cod, db)
    if data.nombre is not None:
        taller.nombre = data.nombre
    if data.direccion is not None:
        taller.direccion = data.direccion
    if data.estado is not None:
        taller.estado = data.estado
    if data.latitud is not None:
        taller.latitud = data.latitud
    if data.longitud is not None:
        taller.longitud = data.longitud
    
    # Sincronizar especialidades
    if data.especialidades is not None:
        await actualizar_especialidades_taller(cod, data.especialidades, db)
    
    await db.commit()
    return await obtener_taller_por_codigo(cod, db)


async def actualizar_disponibilidad(
    cod: str,
    data: DisponibilidadUpdate,
    db: AsyncSession,
) -> TallerOut:
    """CU06 — El taller actualiza su estado operativo."""
    taller = await obtener_taller_por_codigo(cod, db)
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
