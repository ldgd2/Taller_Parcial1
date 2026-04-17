import sys
import os

# Agregamos la ruta base del backend para poder importar los módulos
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

import asyncio
try:
    from app.services.ai_service import analizar_transcripcion_whisper
    from app.core._test_mocks import MOCK_CATEGORIAS, MOCK_PRIORIDADES
except ImportError as e:
    print(f"[ERROR] No se pudo importar los módulos de la aplicación: {e}")
    sys.exit(1)

async def test_openrouter():
    print("Iniciando prueba de Conexión a OpenRouter...")
    texto_prueba = "El carro reventó la llanta delantera, ocupamos un mecánico, estoy en medio de la carretera."
    
    cats = [
        {"id": 1, "nombre": "Falla de Motor"},
        {"id": 2, "nombre": "Llanta Ponchada / Ruedas"},
        {"id": 3, "nombre": "Batería / Eléctrico"}
    ]
    
    prios = [
        {"id": 1, "nombre": "BAJA - Sin Riesgo"},
        {"id": 2, "nombre": "MEDIA - Vehículo inmovilizado"},
        {"id": 3, "nombre": "ALTA - Riesgo de accidente"}
    ]

    print(f"Texto de entrada: {texto_prueba}")
    print("Llamando a la IA...")
    try:
        resultado = await analizar_transcripcion_whisper(texto_prueba, cats, prios)
        print("\n[OK] ¡La IA respondió estructuradamente!")
        print(f">> Resumen: {resultado.resumen}")
        print(f">> ID Categoría: {resultado.id_categoria}")
        print(f">> ID Prioridad: {resultado.id_prioridad}")
        print(f">> Ficha Técnica: {resultado.ficha_tecnica.model_dump()}")
    except Exception as e:
        print(f"[ERROR] Hubo un fallo al conectar con OpenRouter o Instructor: {e}")

if __name__ == "__main__":
    asyncio.run(test_openrouter())
