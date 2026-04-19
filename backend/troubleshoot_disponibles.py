import asyncio
import os
import sys
from dotenv import load_dotenv
import math

# Setup paths
_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_backend_path = os.path.join(_root_dir, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)

load_dotenv(os.path.join(_root_dir, ".env"))

from app.core.database import AsyncSessionLocal
from app.models.taller import Taller
from app.models.emergencia import Emergencia
from app.models.especialidad import Especialidad
from app.models.asignacion_especialidad import AsignacionEspecialidad
from sqlalchemy import select

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

async def troubleshoot_disponibles():
    async with AsyncSessionLocal() as db:
        # 1. Taller
        res_t = await db.execute(select(Taller).where(Taller.cod == "TAL001"))
        taller = res_t.scalar_one_or_none()
        
        if not taller:
            print("[ERROR] Taller TAL001 no encontrado.")
            return
            
        print(f"DEBUG TALLER: {taller.nombre}")
        print(f"   Coords: {taller.latitud}, {taller.longitud}")
        
        # Especialidades del taller
        res_e = await db.execute(
            select(AsignacionEspecialidad.idEspecialidad)
            .where(AsignacionEspecialidad.idTaller == "TAL001")
        )
        especialidades = [r[0] for r in res_e.all()]
        print(f"   Especialidades IDs: {especialidades}")

        # 2. Emergencias
        res_em = await db.execute(select(Emergencia).where(Emergencia.idTaller.is_(None)))
        emergencias = res_em.scalars().all()
        
        print(f"\nDEBUG EMERGENCIAS (Sin Taller Asignado): {len(emergencias)}")
        for e in emergencias:
            dist = 999
            if taller.latitud and taller.longitud and e.latitud and e.longitud:
                dist = haversine(taller.latitud, taller.longitud, e.latitud, e.longitud)
            
            print(f"   - ID {e.id}: Cat {e.idCategoria}, Prio {e.idPrioridad}, Dist {dist:.2f}km")
            print(f"     Coords: {e.latitud}, {e.longitud}")

if __name__ == "__main__":
    asyncio.run(troubleshoot_disponibles())
