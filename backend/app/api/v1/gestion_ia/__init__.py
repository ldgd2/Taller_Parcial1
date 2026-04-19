"""
Package: Gestión IA
──────────────────────────────────────────────────────────────────────────────
Núcleo lógico que procesa los reportes de emergencia, utiliza inteligencia
artificial para clasificar evidencias y ejecuta el motor de asignación
geográfica para conectar al cliente con el taller adecuado.

Casos de Uso:
  CU04 - Reportar Emergencia
  CU08 - Clasificación Automática de Incidentes (IA)
  CU09 - Priorización de Emergencias (IA)
  CU10 - Generar Ficha Técnica (IA / Taller)
  CU11 - Ejecución del Motor de Asignación
  CU12 - Envío de Notificaciones
"""
from fastapi import APIRouter

from .cu04_cu08_cu09_reportar import router as reportar_router
from .cu10_ficha_tecnica import router as ficha_router
from .cu11_motor_asignacion import router as motor_router
from .cu12_notificaciones import router as notif_router

router = APIRouter()
router.include_router(reportar_router)
router.include_router(ficha_router)
router.include_router(motor_router)
router.include_router(notif_router)
