import asyncio
import httpx
import sys
import os

# Agregar 'backend' al path para encontrar 'app'
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal, engine
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.models.tecnico import Tecnico

BASE_URL = "http://localhost:8000/api/v1"

async def test_full_admin_flow():
    print("--- Probando Flujo Completo de Administrador ---")
    
    # 1. Registro
    reg_data = {
        "nombre": "AdminTest",
        "apellido": "Lego",
        "correo": "admintest@lego.com",
        "contrasena": "admin123",
        "nombre_taller": "Taller Lego",
        "direccion_taller": "Calle Lego 123",
        "latitud_taller": -17.7833,
        "longitud_taller": -63.1821
    }
    
    async with httpx.AsyncClient() as client:
        print("\n1. Registrando Administrador...")
        # Limpiar previos
        async with AsyncSessionLocal() as db:
            await db.execute(text("TRUNCATE TABLE tecnico, usuario, taller CASCADE"))
            await db.commit()
        print("[INFO] Limpieza previa completada.")
        
        response = await client.post(f"{BASE_URL}/auth/register", json=reg_data)
        if response.status_code == 409:
             print("[INFO] El usuario ya existe, procediendo al login.")
        elif response.status_code != 200:
            print(f"[FAIL] Error en registro: {response.text}")
            return
        else:
            print("[OK] Registro exitoso.")

        # 2. Login
        print("\n2. Iniciando Sesión...")
        login_data = {
            "correo": reg_data["correo"],
            "contrasena": reg_data["contrasena"],
            "rol": "admin"
        }
        response = await client.post(f"{BASE_URL}/auth/login/web", json=login_data)
        if response.status_code != 200:
            print(f"[FAIL] Error en login: {response.text}")
            return
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("[OK] Login exitoso.")

        # 3. Listar Talleres
        print("\n3. Listando Mis Talleres...")
        response = await client.get(f"{BASE_URL}/talleres/mis-talleres", headers=headers)
        if response.status_code != 200:
            print(f"[FAIL] Error listando talleres: {response.status_code} - {response.text}")
            return
        talleres = response.json()
        print(f"[OK] Talleres encontrados: {len(talleres)}")
        for t in talleres:
            print(f" - {t['nombre']} ({t['cod']}) - Estado: {t['estado']}")
        
        taller_cod = talleres[0]['cod']

        # 4. Crear un segundo taller
        print(f"\n4. Creando un segundo taller para {reg_data['nombre']}...")
        second_taller = {"nombre": "Taller Lego II", "direccion": "Av. Lego 456"}
        response = await client.post(f"{BASE_URL}/talleres/", json=second_taller, headers=headers)
        if response.status_code == 200:
            print(f"[OK] Segundo taller creado: {response.json()['cod']}")
        else:
            print(f"[FAIL] Error creando taller: {response.text}")

        # 5. Registrar un Técnico
        print("\n5. Registrando Técnico en el primer taller...")
        tecnico_data = {
            "nombre": "Mecanico Lego",
            "correo": "mecanico@lego.com",
            "telefono": "12345678",
            "contrasena": "mecanico123",
            "idTaller": taller_cod
        }
        response = await client.post(f"{BASE_URL}/tecnicos/", json=tecnico_data, headers=headers)
        if response.status_code == 200:
            print(f"[OK] Técnico registrado correctamente.")
        else:
            print(f"[FAIL] Error registrando técnico: {response.text}")

        # 6. Listar Técnicos del Taller
        print(f"\n6. Listando técnicos del taller {taller_cod}...")
        response = await client.get(f"{BASE_URL}/tecnicos/taller/{taller_cod}", headers=headers)
        equipo = response.json()
        print(f"[OK] Técnicos encontrados: {len(equipo)}")
        for m in equipo:
            print(f" - {m['nombre']} ({m['correo']})")

    print("\n--- Prueba Finalizada ---")

if __name__ == "__main__":
    asyncio.run(test_full_admin_flow())
