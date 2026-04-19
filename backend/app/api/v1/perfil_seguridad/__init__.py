"""
Package: Gestión Perfil y Seguridad
────────────────────────────────────
Gestiona la autenticación, el control de acceso basado en roles y la
disponibilidad operativa de los talleres.

Casos de Uso:
  CU01 - Gestionar Inicio de Sesión
  CU02 - Gestionar Cierre de Sesión
  CU03 - Registro de Usuario y Vehículo
  CU06 - Gestión de Disponibilidad
  CU07 - Gestionar Técnico
  CU13 - Gestionar Rol
"""
from fastapi import APIRouter

from .cu01_cu02_autenticacion import router as auth_router
from .cu03_clientes import router as clientes_router
from .cu06_disponibilidad import router as disponibilidad_router
from .cu07_cu13_tecnicos import router as tecnicos_router

# Router raíz del paquete — agrupa todos los sub-routers
router = APIRouter()
router.include_router(auth_router)
router.include_router(clientes_router)
router.include_router(disponibilidad_router)
router.include_router(tecnicos_router)
