
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_numeric():
    async with engine.begin() as conn:
        print("Altering table 'pago' to support larger amounts...")
        await conn.execute(text('ALTER TABLE pago ALTER COLUMN "Monto" TYPE NUMERIC(18, 2);'))
        await conn.execute(text('ALTER TABLE pago ALTER COLUMN "MontoComision" TYPE NUMERIC(18, 2);'))
        print("Done.")

if __name__ == "__main__":
    asyncio.run(fix_numeric())
