import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.fcm_token import FCMToken
from app.models.cliente import Cliente

async def check_tokens():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Cliente).limit(5))
        clientes = res.scalars().all()
        print(f"--- Clientes ({len(clientes)}) ---")
        for c in clientes:
            print(f"ID: {c.id}, Nombre: {c.nombre}, Token: {c.fcm_token}")
            
        res_tokens = await db.execute(select(FCMToken))
        tokens = res_tokens.scalars().all()
        print(f"\n--- FCM Tokens ({len(tokens)}) ---")
        for t in tokens:
            print(f"ID: {t.id}, idU: {t.idUsuario}, idC: {t.idCliente}, Token: {t.token[:20]}...")

if __name__ == "__main__":
    asyncio.run(check_tokens())
