import asyncio
import os
import sys
from dotenv import load_dotenv

# Setup paths
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

load_dotenv(os.path.join(_root_dir, ".env"))

from app.core.database import AsyncSessionLocal, engine
from sqlalchemy import text, select
from app.models.emergencia import Emergencia
from app.models.historial_estado import HistorialEstado

async def run_migration():
    print(">> Iniciando migración de idEstado...")
    async with engine.begin() as conn:
        # 1. Agregar columna idEstado a la tabla emergencia si no existe
        # Nota: server_default='1' asume que INICIADA tiene ID 1
        print("   - Verificando columna 'idEstado'...")
        try:
            await conn.execute(text('ALTER TABLE emergencia ADD COLUMN "idEstado" INTEGER DEFAULT 1'))
            await conn.execute(text('ALTER TABLE emergencia ALTER COLUMN "idEstado" SET NOT NULL'))
            await conn.execute(text('ALTER TABLE emergencia ADD CONSTRAINT fk_emergencia_estado FOREIGN KEY ("idEstado") REFERENCES estado(id)'))
            print("   [OK] Columna 'idEstado' creada.")
        except Exception as e:
            if "already exists" in str(e):
                print("   [INFO] La columna 'idEstado' ya existe.")
            else:
                print(f"   [ERROR] No se pudo crear la columna: {e}")

    # 2. Sincronizar datos desde el historial
    async with AsyncSessionLocal() as db:
        print("   - Sincronizando estados desde el historial...")
        res = await db.execute(select(Emergencia))
        emergencias = res.scalars().all()
        
        for e in emergencias:
            # Obtener el historial más reciente
            hist_res = await db.execute(
                select(HistorialEstado)
                .where(HistorialEstado.idEmergencia == e.id)
                .order_by(HistorialEstado.fecha_cambio.desc(), HistorialEstado.id.desc())
                .limit(1)
            )
            last_h = hist_res.scalar_one_or_none()
            if last_h:
                e.idEstado = last_h.idEstado
                print(f"     Emergencia {e.id} -> Estado ID {e.idEstado}")
            else:
                e.idEstado = 1 # PENDIENTE/INICIADA
        
        await db.commit()
        print("[FIN] Datos sincronizados correctamente.")

if __name__ == "__main__":
    asyncio.run(run_migration())
