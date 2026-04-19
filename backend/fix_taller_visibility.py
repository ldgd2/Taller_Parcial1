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
from app.models.taller import Taller
from app.models.especialidad import Especialidad
from app.models.asignacion_especialidad import AsignacionEspecialidad
from sqlalchemy import select

async def fix_visibility():
    async with AsyncSessionLocal() as db:
        # 1. Update TAL001 location (Santa Cruz)
        res_t = await db.execute(select(Taller).where(Taller.cod == "TAL001"))
        taller = res_t.scalar_one_or_none()
        if taller:
            taller.latitud = -17.7833
            taller.longitud = -63.1821
            print(f"[OK] Ubicación de TAL001 actualizada a {taller.latitud}, {taller.longitud}")
        
        # 2. Update Specialties (All)
        res_e = await db.execute(select(Especialidad))
        especialidades = res_e.scalars().all()
        
        for e in especialidades:
            check = await db.execute(
                select(AsignacionEspecialidad).where(
                    AsignacionEspecialidad.idTaller == "TAL001",
                    AsignacionEspecialidad.idEspecialidad == e.id
                )
            )
            if not check.scalar_one_or_none():
                db.add(AsignacionEspecialidad(idTaller="TAL001", idEspecialidad=e.id))
                print(f"   + Especialidad '{e.nombre}' asignada.")

        await db.commit()
        print("\n[FIN] Taller TAL001 listo para recibir emergencias.")

if __name__ == "__main__":
    asyncio.run(fix_visibility())
