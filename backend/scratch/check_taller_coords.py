import asyncio
import sys
import os

# Add parrent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal
from app.models.taller import Taller
from sqlalchemy import select

async def get_taller():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Taller).where(Taller.cod == "TALLER_01"))
        t = res.scalar_one_or_none()
        if t:
            print(f"TALLER_01 -> LAT: {t.latitud}, LNG: {t.longitud}")
        else:
            print("TALLER_01 not found.")

if __name__ == "__main__":
    asyncio.run(get_taller())
