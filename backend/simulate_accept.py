import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.services import emergencia_service
from app.models.emergencia import Emergencia
from app.models.tecnico import Tecnico

async def simulate_accept():
    async with AsyncSessionLocal() as db:
        # 1. Buscar una emergencia pendiente del cliente 17
        res = await db.execute(select(Emergencia).where(Emergencia.idCliente == 17).limit(1))
        e = res.scalar_one_or_none()
        if not e:
            print("No hay emergencias para el cliente 17")
            return
            
        # 2. Buscar un técnico del taller de la emergencia o uno cualquiera
        res_t = await db.execute(select(Tecnico).limit(1))
        t = res_t.scalar_one_or_none()
        if not t:
            print("No hay técnicos")
            return

        print(f"Simulando aceptación de emergencia {e.id} por taller {t.idTaller}")
        try:
            result = await emergencia_service.asignar_emergencia_taller(
                e.id, t.idTaller, [t.id], db
            )
            print(f"Resultado: {result}")
        except Exception as ex:
            print(f"Error en simulación: {ex}")

if __name__ == "__main__":
    asyncio.run(simulate_accept())
