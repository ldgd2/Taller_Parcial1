import asyncio
import asyncpg
import sys
import os

async def test_connection():
    # Datos del .env de la raíz
    user = "postgres"
    password = "Li62156478"
    host = "127.0.0.1"
    port = "5432"
    database = "taller_db"
    
    print(f"Probando conexión a {host}:{port} con usuario {user}...")
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database
        )
        print("[OK] ¡Conexión exitosa via asyncpg!")
        await conn.close()
    except Exception as e:
        print(f"[ERROR] Fallo la conexión: {e}")
        print(f"Tipo: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
