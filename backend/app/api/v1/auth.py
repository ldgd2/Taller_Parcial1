"""
Router de Autenticación — CU01 / CU02
POST /auth/login   → Inicio de sesión
POST /auth/logout  → Cierre de sesión (invalida token en cliente)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.services import auth_service

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse, summary="CU01 — Inicio de sesión")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Autentica un Cliente o Técnico y retorna un JWT.
    - **rol**: `"cliente"` o `"tecnico"`
    """
    return await auth_service.login(data, db)


@router.post("/logout", summary="CU02 — Cierre de sesión")
async def logout(current=Depends(get_current_user)):
    """
    El cliente descarta el token. En una implementación con lista negra
    (blacklist) de JWT, aquí se agregaría el jti a Redis.
    """
    return {"message": "Sesión cerrada correctamente. Descarte el token en el cliente."}
