import asyncio
import sys
import os

# Add parrent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.models.taller import Taller
from sqlalchemy import select

async def ensure_data():
    async with AsyncSessionLocal() as db:
        # Check if TALLER_01 exists
        res = await db.execute(select(Taller).where(Taller.cod == "TALLER_01"))
        taller = res.scalar_one_or_none()
        
        if not taller:
            print("Workshop TALLER_01 missing. Creating...")
            new_taller = Taller(
                cod="TALLER_01",
                nombre="Taller Central de Operaciones",
                direccion="Av. Industrial 555, Planta Alta",
                latitud=-16.5000,
                longitud=-68.1500,
                estado="ACTIVO"
            )
            db.add(new_taller)
            await db.commit()
            print("Workshop TALLER_01 created successfully.")
        else:
            print(f"Workshop TALLER_01 already exists: {taller.nombre}")

if __name__ == "__main__":
    asyncio.run(ensure_data())
