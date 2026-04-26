import asyncio
from sqlalchemy import select, desc
from app.core.database import AsyncSessionLocal
from app.models.emergencia import Emergencia
from app.models.fcm_token import FCMToken

async def check_emergencies():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Emergencia).order_by(desc(Emergencia.id)).limit(5))
        emergencias = res.scalars().all()
        print(f"--- Ultimas Emergencias ---")
        for e in emergencias:
            print(f"ID: {e.id}, ClienteID: {e.idCliente}, Taller: {e.idTaller}, EstadoID: {e.idEstado}")
            
            # Verificar si ese cliente tiene token
            res_t = await db.execute(select(FCMToken).where(FCMToken.idCliente == e.idCliente))
            tokens = res_t.scalars().all()
            print(f"   -> Tokens para Cliente {e.idCliente}: {[t.token[:10] for t in tokens]}")

if __name__ == "__main__":
    asyncio.run(check_emergencies())
