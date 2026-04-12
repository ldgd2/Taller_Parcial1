"""
Servicio de Autenticación — CU01
Valida credenciales de Cliente o Técnico y retorna un JWT.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.cliente import Cliente
from app.models.tecnico import Tecnico
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    if data.rol == "cliente":
        result = await db.execute(select(Cliente).where(Cliente.correo == data.correo))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(data.contrasena, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        token = create_access_token(
            subject=user.id,
            extra_claims={"role": "cliente"},
        )
        return TokenResponse(access_token=token, rol="cliente", nombre=user.nombre)

    elif data.rol == "tecnico":
        result = await db.execute(select(Tecnico).where(Tecnico.correo == data.correo))
        user = result.scalar_one_or_none()
        if user is None or not verify_password(data.contrasena, user.contrasena):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        token = create_access_token(
            subject=user.id,
            extra_claims={"role": "tecnico", "taller": user.idTaller},
        )
        return TokenResponse(access_token=token, rol="tecnico", nombre=user.nombre)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido. Use 'cliente' o 'tecnico'.",
        )
