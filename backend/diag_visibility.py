
import asyncio
import sys
import os

# Añadir el path actual al sys.path para que encuentre 'app'
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.emergencia import Emergencia
from app.models.taller import Taller
from app.models.categoria_problema import CategoriaProblema
from app.models.asignacion_especialidad import AsignacionEspecialidad

async def diag():
    async with AsyncSessionLocal() as db:
        emgs = (await db.execute(select(Emergencia))).scalars().all()
        ts = (await db.execute(select(Taller))).scalars().all()
        
        print("--- EMERGENCIAS ---")
        for e in emgs:
            print(f"ID: {e.id} | Taller: {e.idTaller} | EstadoID: {e.idEstado} | Valida: {e.es_valida} | Lat: {e.latitud} | Lon: {e.longitud}")
            
        print("\n--- TALLERES ---")
        for t in ts:
            esp_res = await db.execute(
                select(AsignacionEspecialidad.idEspecialidad).where(AsignacionEspecialidad.idTaller == t.cod)
            )
            especialidades = [r[0] for r in esp_res.all()]
            print(f"COD: {t.cod} | Nombre: {t.nombre} | Especialidades: {especialidades} | Lat: {t.latitud} | Lon: {t.longitud}")

if __name__ == "__main__":
    asyncio.run(diag())
