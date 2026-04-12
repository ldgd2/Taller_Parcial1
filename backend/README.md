# 🚗 Backend — Plataforma de Emergencias Vehiculares

**FastAPI + SQLAlchemy + PostgreSQL — Ciclo 1**

---

## 📁 Estructura del proyecto

```
backend/
├── main.py                  # Punto de entrada FastAPI
├── init_db.py               # Crea las tablas en la BD
├── seed.py                  # Datos iniciales de catálogo
├── requirements.txt
├── .env.example             # Plantilla de variables de entorno
│
└── app/
    ├── core/
    │   ├── config.py        # Configuración (pydantic-settings)
    │   ├── database.py      # Engine async + sesión + Base
    │   ├── security.py      # bcrypt + JWT
    │   └── dependencies.py  # get_current_user, require_role
    │
    ├── models/              # ORM SQLAlchemy (1 archivo por entidad)
    │   ├── especialidad.py
    │   ├── taller.py
    │   ├── tecnico.py
    │   ├── asignacion_especialidad.py
    │   ├── prioridad.py
    │   ├── categoria_problema.py
    │   ├── estado.py
    │   ├── cliente.py
    │   ├── vehiculo.py
    │   ├── pago.py
    │   ├── emergencia.py
    │   ├── resumen_ia.py
    │   ├── historial_estado.py
    │   └── evidencia.py
    │
    ├── schemas/             # Pydantic (request / response)
    │   ├── auth.py
    │   ├── cliente.py
    │   ├── emergencia.py
    │   └── taller.py
    │
    ├── services/            # Lógica de negocio (sin HTTP)
    │   ├── auth_service.py
    │   ├── cliente_service.py
    │   ├── emergencia_service.py
    │   ├── taller_service.py
    │   └── asignacion_service.py
    │
    └── api/
        └── v1/              # Routers FastAPI
            ├── auth.py
            ├── clientes.py
            ├── emergencias.py
            ├── talleres.py
            └── tecnicos.py
```

---

## ⚙️ Configuración inicial

### 1. Crear entorno virtual e instalar dependencias

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```powershell
copy .env.example .env
# Editar .env con tu cadena de conexión PostgreSQL y SECRET_KEY
```

### 3. Crear la base de datos en PostgreSQL

Ejecuta el script SQL del proyecto (`2.3.2.2.2 Script`) en PostgreSQL primero.

### 4. Crear tablas y cargar datos iniciales

```powershell
python init_db.py
python seed.py
```

### 5. Levantar el servidor

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Accede a la documentación interactiva: **http://localhost:8000/docs**

---

## 🔐 Endpoints — Ciclo 1

| Método | Ruta | Caso de Uso | Rol |
|--------|------|-------------|-----|
| POST | `/api/v1/auth/login` | CU01 — Inicio de sesión | Público |
| POST | `/api/v1/auth/logout` | CU02 — Cierre de sesión | Autenticado |
| POST | `/api/v1/clientes/registro` | CU03 — Registro cliente+vehículo | Público |
| GET | `/api/v1/clientes/mis-vehiculos` | CU03 — Listar vehículos | Cliente |
| POST | `/api/v1/emergencias/reportar` | CU04 + CU11 — Reportar + asignar | Cliente |
| GET | `/api/v1/emergencias/mis-solicitudes` | CU14 — Ver mis solicitudes | Cliente |
| PATCH | `/api/v1/talleres/{cod}/disponibilidad` | CU06 — Disponibilidad taller | Técnico |
| GET | `/api/v1/talleres/{cod}/solicitudes` | CU15 — Solicitudes del taller | Técnico |
| PATCH | `/api/v1/talleres/solicitudes/{id}/estado` | CU15 — Actualizar estado | Técnico |
| GET | `/api/v1/tecnicos/perfil` | Perfil técnico | Técnico |

---

## 🧪 Credenciales de prueba (tras ejecutar seed.py)

| Rol | Correo | Contraseña |
|-----|--------|------------|
| Cliente | `cliente@demo.com` | `cliente123` |
| Técnico | `tecnico@demo.com` | `tecnico123` |

---

## 📋 Ciclos futuros

| Ciclo | Casos de Uso |
|-------|-------------|
| **Ciclo 2** | CU07 (Gestionar Técnico), CU08 (IA Clasificación), CU09 (IA Priorización), CU12 (Notificaciones) |
| **Ciclo 3** | CU02 JWT Blacklist, CU05 (Pagos), CU10 (Ficha Técnica IA), CU13 (Roles) |
