from contextvars import ContextVar
from typing import Optional

# Variables de contexto para rastrear el usuario y la IP en la sesión actual
user_id_ctx: ContextVar[Optional[int]] = ContextVar("user_id_ctx", default=None)
client_ip_ctx: ContextVar[Optional[str]] = ContextVar("client_ip_ctx", default=None)

def set_user_context(user_id: Optional[int]):
    user_id_ctx.set(user_id)

def set_ip_context(ip: Optional[str]):
    client_ip_ctx.set(ip)

def get_user_context() -> Optional[int]:
    return user_id_ctx.get()

def get_ip_context() -> Optional[str]:
    return client_ip_ctx.get()
