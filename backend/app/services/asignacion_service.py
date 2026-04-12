"""
Motor de Asignación Inteligente — CU11
Lógica de Ciclo 1:
  1. Buscar talleres ACTIVOS
  2. Asignar prioridad BAJA por defecto (IA: Ciclo 2)
  3. Asignar categoría genérica (IA: Ciclo 2)
  4. Retornar el taller más adecuado (placeholder geofencing)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.taller import Taller
from app.models.prioridad import Prioridad
from app.models.categoria_problema import CategoriaProblema


async def asignar_taller(db: AsyncSession) -> tuple[str, int, int]:
    """
    Retorna (taller_cod, prioridad_id, categoria_id).
    En Ciclo 1: primer taller ACTIVO / primera prioridad / primera categoría.
    En Ciclo 2 se integrará geofencing e IA.
    """
    # Taller activo
    result = await db.execute(
        select(Taller).where(Taller.estado == "ACTIVO").limit(1)
    )
    taller = result.scalar_one_or_none()
    if taller is None:
        raise ValueError("No hay talleres disponibles en este momento.")

    # Prioridad por defecto (BAJA)
    res_p = await db.execute(select(Prioridad).limit(1))
    prioridad = res_p.scalar_one_or_none()

    # Categoría por defecto (Otros)
    res_c = await db.execute(select(CategoriaProblema).limit(1))
    categoria = res_c.scalar_one_or_none()

    return (
        taller.cod,
        prioridad.id if prioridad else 1,
        categoria.id if categoria else 1,
    )
