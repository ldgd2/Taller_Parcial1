import asyncio
import sys
import os

# Agregar 'backend' al path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import engine
from sqlalchemy import text

async def check_db():
    print("Inspeccionando tabla 'taller'...")
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'taller'"))
        columns = [row[0] for row in res.fetchall()]
        print(f"Columnas en 'taller': {columns}")
        
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'usuario'"))
        columns = [row[0] for row in res.fetchall()]
        print(f"Columnas en 'usuario': {columns}")

if __name__ == "__main__":
    asyncio.run(check_db())
