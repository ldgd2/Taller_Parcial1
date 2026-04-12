"""
Dependencias de autenticación reutilizables para los endpoints protegidos.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Decodifica el JWT y retorna el payload.
    Los routers pueden extraer el 'rol' y el 'sub' (id del usuario).
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise credentials_exc
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise credentials_exc


def require_role(*roles: str):
    """
    Fábrica de dependencias que restringe el acceso por rol.
    Uso: Depends(require_role("taller", "tecnico"))
    """
    async def _check(current=Depends(get_current_user)):
        if current["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permisos para realizar esta acción",
            )
        return current
    return _check
