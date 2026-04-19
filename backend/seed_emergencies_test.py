"""
Seed de Emergencias Procedural — Stress Test Ciclo 1
Genera N emergencias aleatorias en Santa Cruz de la Sierra, 
las pasa por el motor de análisis de IA y el motor de asignación.
"""
import asyncio
import random
import sys
from datetime import datetime
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.cliente import Cliente
from app.models.vehiculo import Vehiculo
from app.schemas.emergencia import EmergenciaCreate
from app.services import emergencia_service

# Pool de problemas técnicos para que la IA trabaje
PROBLEMAS = [
    "Mi auto está echando humo blanco por el capó y se apagó de la nada. Estoy asustado.",
    "Se me pinchó una llanta en plena avenida y no tengo gata ni llanta de auxilio. Ayuda.",
    "La batería parece muerta, no da ni contacto el tablero. Ayer funcionaba bien.",
    "Tuve un choque leve pero el radiador está goteando mucho líquido verde.",
    "El pedal del freno se siente muy blando, como una esponja, y me da miedo seguir frenando.",
    "Siento un ruido metálico muy fuerte en la rueda delantera izquierda al girar.",
    "Me quedé sin gasolina en medio de la carretera, ¿pueden traerme un bidón?",
    "Las luces del tablero parpadean y el auto tironea cuando acelero.",
    "El aire acondicionado dejó de enfriar y sale un olor a quemado de las rejillas.",
    "Se soltó el escape y está arrastrando por el suelo haciendo mucho ruido."
]

# Rango aproximado de Santa Cruz de la Sierra
LAT_MIN, LAT_MAX = -17.850, -17.750
LON_MIN, LON_MAX = -63.250, -63.150

async def seed_procedural(cantidad: int):
    print(f"--- Iniciando Seeder Procedural de {cantidad} emergencias ---")
    
    async with AsyncSessionLocal() as db:
        # 1. Obtener vehículos y sus clientes
        result = await db.execute(
            select(Vehiculo, Cliente)
            .join(Cliente, Vehiculo.idCliente == Cliente.id)
        )
        duplas = result.all()
        
        if not duplas:
            print("[ERROR] No hay vehículos ni clientes en la base de datos. Ejecute seed.py primero.")
            return

        for i in range(cantidad):
            vehiculo, cliente = random.choice(duplas)
            descripcion = random.choice(PROBLEMAS)
            
            # Generar datos aleatorios
            lat = random.uniform(LAT_MIN, LAT_MAX)
            lon = random.uniform(LON_MIN, LON_MAX)
            
            data = EmergenciaCreate(
                descripcion="Emergencia Procedural Test",
                texto_adicional=descripcion,
                direccion=f"Calle Aleatoria Nro {random.randint(1,999)}, Santa Cruz",
                latitud=lat,
                longitud=lon,
                hora=datetime.now().time(),
                placaVehiculo=vehiculo.placa,
                audio_url=None
            )
            
            print(f"[{i+1}/{cantidad}] Reportando emergencia para {vehiculo.placa} (Cliente: {cliente.nombre})...")
            
            try:
                # Llamar al servicio real que usa la IA
                emergencia = await emergencia_service.reportar_emergencia(data, cliente.id, db)
                
                print(f"   -> [OK] ID: {emergencia.id} | Prioridad: {emergencia.idPrioridad} | Taller: {emergencia.idTaller}")
                if emergencia.resumen_ia:
                    print(f"   -> IA Resumen: {emergencia.resumen_ia.resumen[:60]}...")
            except Exception as e:
                print(f"   -> [FALLO] Error procesando emergencia {i+1}: {str(e)}")
            
            # Pequeña pausa para no saturar la API de la IA demasiado rápido si son muchos
            await asyncio.sleep(1)

    print(f"\n--- Seeder finalizado. {cantidad} casos procesados. ---")

if __name__ == "__main__":
    n = 5 # Valor por defecto
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Uso: python seed_emergencies_test.py [cantidad]")
            sys.exit(1)
            
    asyncio.run(seed_procedural(n))
