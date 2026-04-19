import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def test_emergency_flow():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("\n--- 1. Login as Admin A ---")
        # El seed crea 'tecnico@demo.com' pero el admin es el que crea el taller.
        # En el seed pusimos un admin? No, solo un taller y un tecnico.
        # Vamos a crear un admin rápido o usar el taller existente.
        # El login de admin suele ser el usuario que creó el taller.
        
        # Primero, identifiquemos un admin. En el seed, Ana Pérez es cliente.
        # Vamos a registrar un admin real para probar el dashboard.
        
        admin_data = {
            "nombre": "Admin Taller",
            "correo": "admin@taller.com",
            "contrasena": "admin123",
            "nombre_taller": "Taller Mutex Test",
            "direccion_taller": "Av. Mutex 123",
            "latitud_taller": -17.7833,
            "longitud_taller": -63.1821
        }
        
        print("Registrando Admin...")
        reg_res = await client.post(f"{BASE_URL}/auth/register/admin", json=admin_data)
        if reg_res.status_code != 200:
             print(f"Error registro: {reg_res.text}")
        
        # Login
        log_res = await client.post(f"{BASE_URL}/auth/login/web", data={"username": "admin@taller.com", "password": "admin123"})
        token = log_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Obtener cod taller
        taller_res = await client.get(f"{BASE_URL}/talleres/mis-talleres", headers=headers)
        taller_cod = taller_res.json()[0]["cod"]
        print(f"Taller registrado: {taller_cod}")

        print("\n--- 2. Crear Emergencia Cerca (Cliente) ---")
        # Login Cliente (del seed)
        cli_log = await client.post(f"{BASE_URL}/auth/login/mobile", data={"username": "cliente@demo.com", "password": "cliente123"})
        cli_token = cli_log.json()["access_token"]
        cli_headers = {"Authorization": f"Bearer {cli_token}"}
        
        eme_data = {
            "descripcion": "Falla de motor cerca del taller mutex",
            "texto_adicional": "No arranca",
            "direccion": "Cerca Av Mutex",
            "latitud": -17.7840,
            "longitud": -63.1830,
            "placaVehiculo": "DEMO-123",
            "hora": "12:00:00"
        }
        await client.post(f"{BASE_URL}/emergencias/reportar", json=eme_data, headers=cli_headers)

        print("\n--- 3. Ver Emergencias Disponibles ---")
        disp_res = await client.get(f"{BASE_URL}/gestion-emergencia/disponibles", headers=headers)
        emergencias = disp_res.json()
        print(f"Emergencias encontradas: {len(emergencias)}")
        for e in emergencias:
            print(f"  - [{e['id']}] {e['descripcion']} | Locked: {e.get('is_locked', False)}")

        if emergencias:
            target_id = emergencias[0]['id']
            print(f"\n--- 4. Bloquear Emergencia (Análisis) ---")
            await client.post(f"{BASE_URL}/gestion-emergencia/{target_id}/analizar", headers=headers)
            
            # Verificar bloqueo
            disp_res2 = await client.get(f"{BASE_URL}/gestion-emergencia/disponibles", headers=headers)
            e_locked = next(e for e in disp_res2.json() if e['id'] == target_id)
            print(f"  - Bloqueo detectado: {e_locked.get('is_locked')}")

            print("\n--- 5. Asignar Técnico ---")
            # El admin necesita un técnico. El seed creó uno para TAL001, pero este admin tiene su propio taller.
            # Creamos un técnico para este taller.
            tech_data = {
                "nombre": "Tech Mutex",
                "correo": "tech@mutex.com",
                "telefono": "77777777",
                "contrasena": "tech123",
                "idTaller": taller_cod
            }
            tech_res = await client.post(f"{BASE_URL}/tecnicos/", json=tech_data, headers=headers)
            tech_id = tech_res.json()["id"]
            
            # Asignar
            asig_res = await client.post(f"{BASE_URL}/gestion-emergencia/{target_id}/asignar?tecnico_id={tech_id}", headers=headers)
            print(f"Resultado asignación: {asig_res.json()}")

            print("\n--- 6. Verificar que ya no sea disponible ---")
            disp_res3 = await client.get(f"{BASE_URL}/gestion-emergencia/disponibles", headers=headers)
            print(f"Emergencias disponibles ahora: {len(disp_res3.json())}")

if __name__ == "__main__":
    asyncio.run(test_emergency_flow())
