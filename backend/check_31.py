
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.emergencia import Emergencia
from app.models.usuario import Usuario

async def check():
    async with AsyncSessionLocal() as db:
        res_e = await db.execute(select(Emergencia).where(Emergencia.id == 31))
        e = res_e.scalar_one_or_none()
        if e:
            print(f"Emergencia 31 - idTaller: {e.idTaller}")
        else:
            print("Emergencia 31 no encontrada")

        res_u = await db.execute(select(Usuario))
        users = res_u.scalars().all()
        for u in users:
            print(f"Usuario: {u.correo}, Rol: Admin, Taller: {u.idTaller}")

if __name__ == "__main__":
    asyncio.run(check())
