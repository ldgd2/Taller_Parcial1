import asyncio
import sys
import os

# Add parrent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import AsyncSessionLocal as SessionLocal
from app.models.taller import Taller
from app.models.emergencia import Emergencia
from sqlalchemy import select
import json

async def check():
    async with SessionLocal() as db:
        # Check workshops
        res = await db.execute(select(Taller))
        talleres = res.scalars().all()
        print("--- TALLERES ---")
        for t in talleres:
            print(f"COD: {t.cod}, Nombre: {t.nombre}")
        
        # Check one emergency for JSON structure
        res = await db.execute(select(Emergencia).limit(1))
        emg = res.scalar_one_or_none()
        print("\n--- EMERGENCY SAMPLE ---")
        if emg:
            print(f"ID: {emg.id}")
            print(f"Resumen IA: {emg.resumen_ia}")
            print(f"Texto: {emg.texto_adicional}")
        else:
            print("No emergencies found.")

if __name__ == "__main__":
    asyncio.run(check())
