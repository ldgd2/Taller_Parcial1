import instructor
from openai import AsyncOpenAI
import json
from app.core.config import settings
from app.schemas.ai_schemas import AnalisisEstructuradoIA

# Initialize the client with OpenRouter
client = instructor.from_openai(AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
))

async def analizar_transcripcion_whisper(
    texto_crudo: str, 
    vehiculo_info: str,
    categorias_disponibles: list[dict], 
    prioridades_disponibles: list[dict]
) -> AnalisisEstructuradoIA:
    """
    Analiza el texto de una emergencia y extrae de forma estructurada
    la categoría, prioridad, resumen y ficha técnica preliminar para el mecánico.
    """
    
    # Formatear el contexto para el prompt
    cat_str = json.dumps(categorias_disponibles, ensure_ascii=False)
    pri_str = json.dumps(prioridades_disponibles, ensure_ascii=False)
    
    system_prompt = f"""
Eres un experto en peritaje mecánico vehicular de alta precisión.
Tu misión es generar una ficha técnica accionable para que un TALLER MECÁNICO se prepare antes de salir al auxilio.

VEHÍCULO DEL CLIENTE: {vehiculo_info}

CATEGORÍAS DISPONIBLES (Usa el ID exacto):
{cat_str}

PRIORIDADES DISPONIBLES (Usa el ID exacto):
{pri_str}

Instrucciones Críticas para el JSON:
1. 'titulo_emergencia': Genera un título corto y profesional (Ej: "Falla en Bomba de Combustible", "Sobrecalentamiento Crítico").
2. 'resumen_taller': Redacta un resumen breve pero TÉCNICO de lo que el mecánico encontrará.
3. 'diagnostico_probable': Basado en síntomas y el modelo de auto, propón la falla más lógica.
4. 'piezas_necesarias': Componentes del vehículo que podrían estar comprometidos.
5. 'repuestos_sugeridos': Qué debe subir el taller a la unidad de servicio (Ej: "Aceite 5W30", "Batería 12V 70Ah").
6. 'protocolo_tecnico': Instrucciones específicas para el TÉCNICO al llegar (Ej: "No encender el motor", "Revisar presión de riel").
7. Selecciona el 'id_categoria' e 'id_prioridad' que mejor correspondan.
"""

    response: AnalisisEstructuradoIA = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL_NAME,
        response_model=AnalisisEstructuradoIA,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"REPORTE DEL CLIENTE: {texto_crudo}"},
        ],
        max_retries=3
    )

    return response
