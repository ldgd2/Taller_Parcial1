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

from app.core.database import AsyncSessionLocal
from app.services import emergencia_service
from app.schemas.emergencia import EmergenciaOut

async def verify_status():
    async with AsyncSessionLocal() as db:
        print(">> Consultando emergencias disponibles para TAL001...")
        emergencias = await emergencia_service.listar_emergencias_disponibles("TAL001", db)
        
        if not emergencias:
            print("[WARN] No hay emergencias disponibles para TAL001.")
            return

        for e in emergencias:
            # Validar con Pydantic
            out = EmergenciaOut.model_validate(e)
            print(f"[OK] Emergencia ID {out.id}:")
            print(f"     Estado Actual: {out.estado_actual}")
            print(f"     Locked: {out.is_locked}")
            
if __name__ == "__main__":
    asyncio.run(verify_status())
