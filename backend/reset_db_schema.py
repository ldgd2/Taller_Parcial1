import asyncio
import platform
import sys
import os

# Añadir el padre al path para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import engine, Base
from app.models import *

async def reset_schema():
    print("Borrando tablas existentes...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Recreando esquema...")
        await conn.run_sync(Base.metadata.create_all)
    print("Esquema reseteado correctamente.")

if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reset_schema())
