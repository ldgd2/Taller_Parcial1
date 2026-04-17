from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.especialidad import Especialidad
from app.models.estado import Estado
from app.models.prioridad import Prioridad
from app.models.categoria_problema import CategoriaProblema
from app.schemas.catalogos import (
    EspecialidadCreate, EstadoCreate, PrioridadCreate, CategoriaProblemaCreate
)

# Especialidad
async def crear_especialidad(data: EspecialidadCreate, db: AsyncSession):
    obj = Especialidad(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def listar_especialidades(db: AsyncSession):
    res = await db.execute(select(Especialidad))
    return res.scalars().all()

# Estado
async def crear_estado(data: EstadoCreate, db: AsyncSession):
    obj = Estado(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj

async def listar_estados(db: AsyncSession):
    res = await db.execute(select(Estado))
    return res.scalars().all()

# Prioridad
async def listar_prioridades(db: AsyncSession):
    res = await db.execute(select(Prioridad))
    return res.scalars().all()

# Categoria
async def listar_categorias(db: AsyncSession):
    res = await db.execute(select(CategoriaProblema))
    return res.scalars().all()
