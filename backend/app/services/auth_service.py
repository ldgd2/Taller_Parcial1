"""
Servicio de Autenticación — CU01
Valida credenciales de Cliente o Técnico y retorna un JWT.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.cliente import Cliente
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.models.taller import Taller
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.auth import LoginRequest, TokenResponse, RegisterAdminRequest
import random
import string
import re


def generate_workshop_code(name: str) -> str:
    """Generat a 10-char code based on name + 4 random chars."""
    # Clean name: only letters and numbers
    clean_name = re.sub(r'[^A-Z0-9]', '', name.upper())
    base = clean_name[:6]
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    # Ensure it's exactly 10 chars, padding with random if name too short
    code = base.ljust(6, 'X')[:6] + random_suffix
    return code


async def register_admin(data: RegisterAdminRequest, db: AsyncSession) -> Usuario:
    """Registra un nuevo administrador y su taller."""
    try:
        # 1. Verificar si el correo ya existe en alguna tabla de usuarios
        result = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo electrónico ya está registrado.",
            )

        # 2. Crear el Taller
        workshop_cod = generate_workshop_code(data.nombre_taller)
        
        taller = Taller(
            cod=workshop_cod,
            nombre=data.nombre_taller,
            direccion=data.direccion_taller,
            latitud=data.latitud_taller,
            longitud=data.longitud_taller,
            estado="ACTIVO"
        )
        db.add(taller)
        await db.flush()

        # 3. Crear el Usuario Administrador
        usuario = Usuario(
            nombre=data.nombre,
            apellido=data.apellido,
            correo=data.correo,
            contrasena=hash_password(data.contrasena),
            estado="ACTIVO",
            idTaller=taller.cod
        )
        db.add(usuario)
        await db.flush()
        
        taller.id_admin = usuario.id
        await db.commit()
        await db.refresh(usuario)
        return usuario
    except Exception as e:
        import traceback
        error_msg = f"Error en register_admin: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("error_log.txt", "a") as f:
            f.write(error_msg + "\n")
        raise HTTPException(status_code=500, detail=str(e))


async def login(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """Login para la aplicación móvil (Clientes y Técnicos)."""
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
        return TokenResponse(access_token=token, rol="tecnico", nombre=user.nombre, cod_taller=user.idTaller)

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rol inválido para login móvil. Use 'cliente' o 'tecnico'.",
        )


async def login_web(data: LoginRequest, db: AsyncSession) -> TokenResponse:
    """Login para la aplicación web (Administradores de Taller)."""
    if data.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Este portal es solo para administradores.",
        )

    result = await db.execute(select(Usuario).where(Usuario.correo == data.correo))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.contrasena, user.contrasena):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )
    
    token = create_access_token(
        subject=user.id,
        extra_claims={"role": "admin", "taller": user.idTaller},
    )
    return TokenResponse(access_token=token, rol="admin", nombre=user.nombre, cod_taller=user.idTaller)
