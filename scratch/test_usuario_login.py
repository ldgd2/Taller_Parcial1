import asyncio
import sys
import os

# Añadir el path del backend para poder importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, engine
from app.models.taller import Taller
from app.models.usuario import Usuario
from app.core.security import hash_password
from app.services import auth_service
from app.schemas.auth import LoginRequest

async def test_usuario_login():
    async with AsyncSessionLocal() as db:
        print("--- Iniciando prueba de Usuario y Login ---")
        
        # 1. Limpiar datos previos si existen
        await db.execute(delete(Usuario).where(Usuario.correo == "admin@test.com"))
        await db.execute(delete(Taller).where(Taller.cod == "TEST01"))
        await db.commit()

        # 2. Crear Taller de prueba
        taller = Taller(
            cod="TEST01",
            nombre="Taller de Prueba",
            direccion="Calle Falsa 123",
            estado="ACTIVO"
        )
        db.add(taller)
        await db.commit()
        print(f"Taller creado: {taller.cod}")

        # 3. Crear Usuario admin de prueba
        usuario = Usuario(
            nombre="Admin",
            apellido="Prueba",
            correo="admin@test.com",
            contrasena=hash_password("password123"),
            estado="ACTIVO",
            idTaller="TEST01"
        )
        db.add(usuario)
        await db.commit()
        print(f"Usuario admin creado: {usuario.correo}")

        # 4. Probar Login
        login_data = LoginRequest(
            correo="admin@test.com",
            contrasena="password123",
            rol="admin"
        )
        
        try:
            response = await auth_service.login(login_data, db)
            print("Login exitoso!")
            print(f"Token: {response.access_token[:30]}...")
            print(f"Rol: {response.rol}")
            print(f"Nombre: {response.nombre}")
            
            # Verificar que el login falló con contraseña incorrecta
            login_data_bad = LoginRequest(
                correo="admin@test.com",
                contrasena="wrongpassword",
                rol="admin"
            )
            try:
                await auth_service.login(login_data_bad, db)
                print("ERROR: El login debería haber fallado con contraseña incorrecta")
            except Exception as e:
                print(f"Verificación exitosa: Fallo esperado con contraseña incorrecta ({e.detail})")

        except Exception as e:
            print(f"Error en login: {e}")

        # Limpieza
        await db.execute(delete(Usuario).where(Usuario.correo == "admin@test.com"))
        await db.execute(delete(Taller).where(Taller.cod == "TEST01"))
        await db.commit()
        print("Limpieza completada.")

if __name__ == "__main__":
    asyncio.run(test_usuario_login())
