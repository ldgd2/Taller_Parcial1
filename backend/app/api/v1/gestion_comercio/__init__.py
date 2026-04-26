"""
Package: Gestión Comercio
──────────────────────────────────────────────────────────────────────────────
Administra el flujo de solicitudes de servicio, el historial de incidentes y
las transacciones financieras, garantizando la trazabilidad del trabajo
realizado y la correcta ejecución de los pagos.

Casos de Uso:
  CU05 - Gestionar Tipo de Pago
  CU14 - Gestión de Solicitud Cliente
  CU15 - Gestión de Solicitud Taller
"""
from fastapi import APIRouter

from .cu05_pagos import router as pagos_router
from .cu14_solicitudes_cliente import router as solicitudes_cliente_router
from .cu15_solicitudes_taller import router as solicitudes_taller_router
from .cu12_notificaciones import router as notificaciones_router
from .cu17_facturacion import router as facturacion_router
from .cu18_reportes import router as reportes_router

router = APIRouter()
router.include_router(pagos_router)
router.include_router(solicitudes_cliente_router)
router.include_router(solicitudes_taller_router)
router.include_router(notificaciones_router)
router.include_router(facturacion_router)
router.include_router(reportes_router)
