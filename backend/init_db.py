"""
Script de inicialización de tablas para desarrollo.
Crea todas las tablas en la base de datos si no existen.
Para producción usar Alembic migrations.
"""
import asyncio
from app.core.database import engine, Base
from app.models import *  # noqa: F401, F403


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas correctamente.")


if __name__ == "__main__":
    asyncio.run(init_db())
