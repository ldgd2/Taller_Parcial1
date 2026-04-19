import asyncio
import sys
import os

# Agregar 'backend' al path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.core.database import engine, Base
from app.models import *
from sqlalchemy import text

async def reset_db():
    print("RESENTANDO BASE DE DATOS COMPLETAMENTE...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        
        print("Creando tablas desde cero...")
        await conn.run_sync(Base.metadata.create_all)
        
        # Doble verificación/forzado
        try:
            await conn.execute(text("ALTER TABLE taller ADD COLUMN IF NOT EXISTS id_admin INTEGER"))
            print("Columna id_admin asegurada.")
        except Exception as e:
            print(f"Nota: {e}")
            
    print("Base de datos reseteada correctamente.")

if __name__ == "__main__":
    asyncio.run(reset_db())
