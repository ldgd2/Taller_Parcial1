import asyncio
from app.core.database import AsyncSessionLocal
from app.models.estado import Estado
from sqlalchemy import select

async def run():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Estado))
        for e in res.scalars().all():
            print(f"{e.id}: {e.nombre}")

if __name__ == "__main__":
    asyncio.run(run())
