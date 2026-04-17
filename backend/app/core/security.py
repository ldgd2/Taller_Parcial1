"""
Utilidades de seguridad:
  - Hashing de contraseñas (bcrypt)
  - Generación y verificación de JWT
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
import bcrypt
from app.core.config import settings

# ─── Contraseñas ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Encripta una contraseña usando bcrypt nativo."""
    # bcrypt requiere bytes, codificamos el salt y el password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash."""
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


# ─── JWT ──────────────────────────────────────────────────────────

def create_access_token(subject: Any, extra_claims: dict | None = None) -> str:
    """
    Crea un JWT.
    :param subject: identificador del usuario (id o correo)
    :param extra_claims: campos adicionales a incluir en el payload
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(subject), "exp": expire}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decodifica un JWT. Lanza JWTError si es inválido o expirado.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
