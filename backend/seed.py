"""
Script de datos iniciales (Seed) — Ciclo 1
Crea los registros de catálogo base que el sistema necesita para funcionar:
  - Estados
  - Prioridades
  - Categorías de Problema
  - Un taller de prueba
  - Un técnico de prueba
  - Un cliente de prueba
"""
import asyncio
import platform
import warnings
from sqlalchemy import text
from app.core.database import AsyncSessionLocal, engine, Base
from app.core.security import hash_password
from app.models.estado import Estado
from app.models.prioridad import Prioridad
from app.models.categoria_problema import CategoriaProblema
from app.models.taller import Taller
from app.models.tecnico import Tecnico
from app.models.cliente import Cliente
from app.models.vehiculo import Vehiculo

# Silenciar el aviso de deprecación de loop policy en Python 3.14+
warnings.filterwarnings("ignore", category=DeprecationWarning)

async def ensure_db_initialized():
    """Crea las tablas si no existen antes de sembrar."""
    from init_db import check_and_create_db
    await check_and_create_db()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def seed():
    await ensure_db_initialized()
    async with AsyncSessionLocal() as db:
        # ── Estados ──────────────────────────────────────────────
        estados = [
            Estado(nombre="INICIADA",    descripcion="Reporte sugerido por el usuario, pendiente de análisis IA"),
            Estado(nombre="PENDIENTE",   descripcion="Solicitud analizada, en espera de asignación de taller"),
            Estado(nombre="ENVIADA",     descripcion="Notificación enviada al taller para aceptación"),
            Estado(nombre="ASIGNADO",    descripcion="Taller y técnico asignados a la emergencia"),
            Estado(nombre="EN_PROCESO",  descripcion="Técnico en camino o atendiendo"),
            Estado(nombre="ATENDIDO",    descripcion="Servicio completado"),
            Estado(nombre="CANCELADO",   descripcion="Solicitud cancelada"),
            Estado(nombre="FINALIZADA",  descripcion="Emergencia pagada y cerrada"),
        ]
        for e in estados:
            result = await db.execute(
                text("SELECT 1 FROM estado WHERE nombre = :n"), {"n": e.nombre}
            )
            if not result.fetchone():
                db.add(e)

        # ── Especialidades ────────────────────────────────────────
        from app.models.especialidad import Especialidad
        esp_mecanica = Especialidad(nombre="Mecánica General", descripcion="Reparación de motor y sistemas generales")
        esp_grua = Especialidad(nombre="Grúa y Remolque", descripcion="Servicio de traslado de vehículos")
        esp_llanteria = Especialidad(nombre="Llantería", descripcion="Reparación y cambio de neumáticos")
        esp_bateria = Especialidad(nombre="Sistema Eléctrico / Batería", descripcion="Servicio de batería y electricidad")

        result = await db.execute(text("SELECT COUNT(*) FROM especialidad"))
        if result.scalar() == 0:
            db.add_all([esp_mecanica, esp_grua, esp_llanteria, esp_bateria])
            await db.flush()

        # ── Prioridades ───────────────────────────────────────────
        prioridades = [
            Prioridad(descripcion="BAJA"),
            Prioridad(descripcion="MEDIA"),
            Prioridad(descripcion="ALTA"),
            Prioridad(descripcion="CRÍTICA"),
        ]
        result = await db.execute(text("SELECT COUNT(*) FROM prioridad"))
        if result.scalar() == 0:
            db.add_all(prioridades)

        # ── Categorías ──────────────────────────────────────────── (Vinculadas a Especialidad)
        categorias = [
            CategoriaProblema(descripcion="Batería", idEspecialidad=4), # esp_bateria
            CategoriaProblema(descripcion="Llanta", idEspecialidad=3),  # esp_llanteria
            CategoriaProblema(descripcion="Choque", idEspecialidad=2),  # esp_grua
            CategoriaProblema(descripcion="Motor", idEspecialidad=1),   # esp_mecanica
            CategoriaProblema(descripcion="Otros", idEspecialidad=1),   # esp_mecanica default
        ]
        result = await db.execute(text("SELECT COUNT(*) FROM categoria_problema"))
        if result.scalar() == 0:
            db.add_all(categorias)

        # ── Taller de prueba ──────────────────────────────────────
        result = await db.execute(text("SELECT 1 FROM taller WHERE cod = 'TAL001'"))
        if not result.fetchone():
            taller = Taller(
                cod="TAL001",
                nombre="Taller Central Demo",
                direccion="Av. Principal 123, Santa Cruz",
                estado="ACTIVO",
            )
            db.add(taller)
            await db.flush()

            # ── Técnico de prueba ─────────────────────────────────
            tecnico = Tecnico(
                nombre="Carlos Flores",
                correo="tecnico@demo.com",
                contrasena=hash_password("tecnico123"),
                telefono="70000001",
                idTaller="TAL001",
            )
            db.add(tecnico)

        # ── Cliente de prueba ─────────────────────────────────────
        result = await db.execute(
            text("SELECT 1 FROM cliente WHERE correo = 'cliente@demo.com'")
        )
        if not result.fetchone():
            cliente = Cliente(
                nombre="Ana Pérez",
                correo="cliente@demo.com",
                contrasena=hash_password("cliente123"),
            )
            db.add(cliente)
            await db.flush()

            vehiculo = Vehiculo(
                placa="DEMO-123",
                marca="Toyota",
                modelo="Corolla",
                anio=2020,
                idCliente=cliente.id,
            )
            db.add(vehiculo)

        await db.commit()
        print("[OK] Seed completado exitosamente.")
        print("\nCredenciales de prueba:")
        print("  Cliente  -> correo: cliente@demo.com  | pass: cliente123  | rol: cliente")
        print("  Tecnico  -> correo: tecnico@demo.com  | pass: tecnico123  | rol: tecnico")


if __name__ == "__main__":
    asyncio.run(seed())
