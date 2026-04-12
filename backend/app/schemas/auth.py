from pydantic import BaseModel, EmailStr


# ─── Login ───────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    correo: EmailStr
    contrasena: str
    rol: str  # "cliente" | "tecnico"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: str
    nombre: str
