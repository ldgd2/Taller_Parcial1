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
    categorias_disponibles: list[dict], 
    prioridades_disponibles: list[dict]
) -> AnalisisEstructuradoIA:
    """
    Analiza el texto de una emergencia y extrae de forma estructurada
    la categoría, prioridad, resumen y ficha técnica preliminar.
    """
    
    # Formatear el contexto para el prompt
    cat_str = json.dumps(categorias_disponibles, ensure_ascii=False)
    pri_str = json.dumps(prioridades_disponibles, ensure_ascii=False)
    
    system_prompt = f"""
Eres un experto en peritaje mecánico vehicular de alta precisión.
Tu misión es analizar el reporte de un conductor en apuros y generar una ficha técnica accionable para que un TALLER MECÁNICO se prepare antes de salir al auxilio.

CATEGORÍAS DISPONIBLES (Usa el ID exacto):
{cat_str}

PRIORIDADES DISPONIBLES (Usa el ID exacto):
{pri_str}

Instrucciones Críticas:
1. 'resumen_taller': Redacta un resumen breve pero TÉCNICO de lo que el mecánico encontrará (Ej: "Posible sobrecalentamiento con fuga de refrigerante en manguera superior").
2. 'diagnostico_probable': Basado en los síntomas (humo, ruidos, luces del tablero), propón la falla más lógica.
3. 'piezas_necesarias': Enumera qué partes internas del vehículo podrían estar comprometidas.
4. 'repuestos_sugeridos': Lista de repuestos que el taller debe subir a la unidad de servicio (Ej: "Kit de mangueras", "Fusibles de 20A", "Líquido hidráulico").
5. 'acciones_inmediatas': Instrucciones de seguridad vitales para el conductor.
6. Selecciona el 'id_categoria' e 'id_prioridad' que mejor correspondan.
"""

    response: AnalisisEstructuradoIA = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL_NAME,
        response_model=AnalisisEstructuradoIA,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texto_crudo},
        ],
        max_retries=3
    )

    return response
