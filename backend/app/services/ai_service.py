import instructor
from openai import AsyncOpenAI
import json
from app.core.config import settings
from app.schemas.ai_schemas import AnalisisEstructuradoIA, SimulacionCostoIA

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

Instrucciones Críticas de Validación y Formato:
1. 'es_valida': Evalúa si el reporte es una falla mecánica real de un vehículo. Si el usuario envía bromas, pide código de programación, habla de temas no mecánicos o el texto no tiene sentido automotriz, marca FALSE.
2. 'motivo_rechazo': Si 'es_valida' es FALSE, especifica la razón (Ej: "El usuario está solicitando código Python", "Reporte fuera de contexto automotriz").
3. 'recomendaciones_taller': Proporciona consejos estratégicos para el mecánico (Ej: "Este modelo de BMW suele tener problemas con el sensor X al recalentar, llevar escáner específico", "El cliente parece alterado, mantener comunicación calmada").
4. 'titulo_emergencia': Genera un título corto y profesional.
5. 'resumen_taller': Redacta un resumen técnico EXCLUSIVO para el taller.
6. 'diagnostico_probable': Basado en síntomas y el modelo de auto, propón la falla más lógica.
7. 'piezas_necesarias' y 'repuestos_sugeridos': Lista componentes y repuestos que el taller debe preparar.
8. 'protocolo_tecnico': Instrucciones específicas para el TÉCNICO al llegar.
9. Selecciona el 'id_categoria' e 'id_prioridad' que mejor correspondan.
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

async def simular_costo_servicio(
    texto_crudo: str, 
    vehiculo_info: str,
    distancia_estimada: float = 0.0
) -> SimulacionCostoIA:
    """
    Simula el costo de un servicio mecánico basado en la descripción, 
    el vehículo y precios de mercado.
    """
    
    system_prompt = f"""
Eres un analista de costos para servicios mecánicos automotrices.
Tu tarea es simular un presupuesto justo basado en:
1. VEHÍCULO: {vehiculo_info}
2. DISTANCIA AL TALLER: {distancia_estimada} km
3. MERCADO: Precios estándar para repuestos y mano de obra en 2024.

INSTRUCCIONES:
- 'mano_de_obra': Debe incluir el costo base por diagnóstico y el servicio. Considera la complejidad del auto.
- 'repuestos_estimados': Identifica qué piezas podrían necesitar cambio y ponles un precio real de mercado.
- 'comision_sistema': DEBE SER EXACTAMENTE EL 10% de (Mano de obra + Repuestos).
- 'total_estimado': Suma de todos los rubros.
- 'justificacion_mercado': Explica brevemente por qué el precio es ese (Ej: "El kit de distribución para este Audi es premium", "La distancia de 20km influye en el costo de traslado").
"""

    response: SimulacionCostoIA = await client.chat.completions.create(
        model=settings.OPENROUTER_MODEL_NAME,
        response_model=SimulacionCostoIA,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"FALLA REPORTADA: {texto_crudo}"},
        ],
        max_retries=3
    )

    return response
