import asyncio
import sys
import os

# Añadir el path del backend para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.models.cliente import Cliente
from app.core.security import hash_password
from app.services import auth_service
from app.schemas.auth import LoginRequest

async def test_split_login():
    async with AsyncSessionLocal() as db:
        print("--- Iniciando prueba de Login Dividido ---")
        
        # 1. Preparar datos
        await db.execute(delete(Usuario).where(Usuario.correo == "admin@test.com"))
        await db.execute(delete(Cliente).where(Cliente.correo == "cliente@test.com"))
        await db.execute(delete(Taller).where(Taller.cod == "TEST01"))
        await db.commit()

        taller = Taller(cod="TEST01", nombre="Taller Prueba", direccion="Calle 1", estado="ACTIVO")
        admin = Usuario(nombre="Admin", apellido="Prueba", correo="admin@test.com", 
                        contrasena=hash_password("admin123"), estado="ACTIVO", idTaller="TEST01")
        cliente = Cliente(nombre="Cliente", correo="cliente@test.com", 
                          contrasena=hash_password("cliente123"), estado="ACTIVO")
        
        db.add(taller)
        db.add(admin)
        db.add(cliente)
        await db.commit()

        # 2. Pruebas de Web (/auth/login/web)
        print("\nPruebas de Web (/auth/login/web):")
        
        # Admin en Web -> Debe funcionar
        try:
            res = await auth_service.login_web(LoginRequest(correo="admin@test.com", contrasena="admin123", rol="admin"), db)
            print("[OK] Admin logueado correctamente en Web")
        except Exception as e:
            print(f"[FAIL] Admin falló en Web: {e}")

        # Cliente en Web -> Debe fallar (403 Forbidden)
        try:
            await auth_service.login_web(LoginRequest(correo="cliente@test.com", contrasena="cliente123", rol="cliente"), db)
            print("[FAIL] Cliente logró loguearse en Web!")
        except Exception as e:
            print(f"[OK] Cliente rechazado en Web ({e.detail})")

        # 3. Pruebas de Móvil (/auth/login)
        print("\nPruebas de Móvil (/auth/login):")
        
        # Cliente en Móvil -> Debe funcionar
        try:
            res = await auth_service.login(LoginRequest(correo="cliente@test.com", contrasena="cliente123", rol="cliente"), db)
            print("[OK] Cliente logueado correctamente en Móvil")
        except Exception as e:
            print(f"[FAIL] Cliente falló en Móvil: {e}")

        # Admin en Móvil -> Debe fallar (400 Bad Request)
        try:
            await auth_service.login(LoginRequest(correo="admin@test.com", contrasena="admin123", rol="admin"), db)
            print("[FAIL] Admin logró loguearse en Móvil!")
        except Exception as e:
            print(f"[OK] Admin rechazado en Móvil ({e.detail})")

        # Limpieza
        await db.execute(delete(Usuario).where(Usuario.correo == "admin@test.com"))
        await db.execute(delete(Cliente).where(Cliente.correo == "cliente@test.com"))
        await db.execute(delete(Taller).where(Taller.cod == "TEST01"))
        await db.commit()
        print("\nLimpieza completada.")

if __name__ == "__main__":
    asyncio.run(test_split_login())
