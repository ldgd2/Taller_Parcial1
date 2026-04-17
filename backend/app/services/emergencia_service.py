"""
Servicio de Emergencias — CU04, CU14, CU15
  CU04: Reportar emergencia (cliente)
  CU14: Consultar mis solicitudes (cliente)
  CU15: Gestionar solicitud taller (taller — aceptar/rechazar/actualizar estado)
"""
import datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.emergencia import Emergencia
from app.models.historial_estado import HistorialEstado
from app.models.estado import Estado
from app.models.vehiculo import Vehiculo
from app.models.prioridad import Prioridad
from app.models.categoria_problema import CategoriaProblema
from app.models.resumen_ia import ResumenIA
from app.schemas.emergencia import EmergenciaCreate, EmergenciaOut, ActualizarEstadoRequest
from app.services.asignacion_service import asignar_taller
from app.services.ai_service import analizar_transcripcion_whisper


# ─── CU04 ─────────────────────────────────────────────────────────

async def reportar_emergencia(
    data: EmergenciaCreate,
    cliente_id: int,
    db: AsyncSession,
) -> EmergenciaOut:
    # Validar que el vehículo pertenece al cliente
    res = await db.execute(
        select(Vehiculo).where(
            Vehiculo.placa == data.placaVehiculo,
            Vehiculo.idCliente == cliente_id,
        )
    )
    if res.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece al cliente.",
        )

    # Motor de asignación base (CU11)
    taller_cod, default_prioridad_id, default_categoria_id = await asignar_taller(db)

    # Variables finales
    prioridad_id = default_prioridad_id
    categoria_id = default_categoria_id
    resumen_taller = ""
    ficha_tecnica = None

    # CU08, CU09, CU10: IA processing si hay texto
    if data.texto_adicional:
        try:
            # Obtener catálogos para el prompt de IA
            cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.nombre))
            prios_res = await db.execute(select(Prioridad.id, Prioridad.nombre))
            
            categorias_activas = [{"id": r.id, "nombre": r.nombre} for r in cats_res.all()]
            prioridades_activas = [{"id": r.id, "nombre": r.nombre} for r in prios_res.all()]

            # Llamada al servicio de IA OpenRouter + Instructor
            ia_result = await analizar_transcripcion_whisper(
                texto_crudo=data.texto_adicional,
                categorias_disponibles=categorias_activas,
                prioridades_disponibles=prioridades_activas
            )

            # Reemplazar valores base con los dictaminados por la IA
            prioridad_id = ia_result.id_prioridad
            categoria_id = ia_result.id_categoria
            resumen_taller = ia_result.resumen_taller
            ficha_tecnica = ia_result.ficha_tecnica.model_dump()
        except Exception as e:
            print(f"Error procesando IA: {e}")
            # Si la IA falla, usamos los defaults y seguimos sin interrumpir la emergencia crítica

    # Crear emergencia
    emergencia = Emergencia(
        descripcion=data.descripcion,
        texto_adicional=data.texto_adicional,
        direccion=data.direccion,
        latitud=data.latitud,
        longitud=data.longitud,
        fecha=datetime.date.today(),
        hora=data.hora,
        idTaller=taller_cod,
        idPrioridad=prioridad_id,
        idCategoria=categoria_id,
        idCliente=cliente_id,
        placaVehiculo=data.placaVehiculo,
    )
    db.add(emergencia)
    await db.flush()

    # Guardar análisis IA si fue procesado
    if resumen_taller:
        resumen_ia = ResumenIA(
            resumen=resumen_taller,
            ficha_tecnica=ficha_tecnica,
            idEmergencia=emergencia.id
        )
        db.add(resumen_ia)
        await db.flush()

    # Registrar estado inicial → PENDIENTE
    estado_res = await db.execute(select(Estado).where(Estado.nombre == "PENDIENTE"))
    estado = estado_res.scalar_one_or_none()
    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Estado 'PENDIENTE' no encontrado en BD. Ejecute el seed inicial.",
        )

    historial = HistorialEstado(
        idEmergencia=emergencia.id,
        idEstado=estado.id,
    )
    db.add(historial)
    await db.flush()

    return EmergenciaOut(
        id=emergencia.id,
        descripcion=emergencia.descripcion,
        texto_adicional=emergencia.texto_adicional,
        ubicacion=emergencia.ubicacion,
        fecha=emergencia.fecha,
        hora=emergencia.hora,
        idTaller=emergencia.idTaller,
        idPrioridad=emergencia.idPrioridad,
        idCategoria=emergencia.idCategoria,
        estado_actual="PENDIENTE",
    )


# ─── CU14 (cliente consulta sus emergencias) ──────────────────────

async def listar_emergencias_cliente(cliente_id: int, db: AsyncSession):
    result = await db.execute(
        select(Emergencia)
        .where(Emergencia.idCliente == cliente_id)
        .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
    )
    return result.scalars().all()


# ─── CU15 (taller actualiza el estado de la emergencia) ──────────

async def actualizar_estado_emergencia(
    emergencia_id: int,
    data: ActualizarEstadoRequest,
    taller_cod: str,
    db: AsyncSession,
) -> HistorialEstado:
    # Verificar que la emergencia pertenece al taller
    res = await db.execute(
        select(Emergencia).where(
            Emergencia.id == emergencia_id,
            Emergencia.idTaller == taller_cod,
        )
    )
    emergencia = res.scalar_one_or_none()
    if emergencia is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergencia no encontrada o no asignada a este taller.",
        )

    # Verificar que el estado existe
    res_est = await db.execute(select(Estado).where(Estado.id == data.idEstado))
    if res_est.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estado no válido.",
        )

    nuevo_historial = HistorialEstado(
        idEmergencia=emergencia_id,
        idEstado=data.idEstado,
    )
    db.add(nuevo_historial)
    await db.flush()
    return nuevo_historial


async def listar_emergencias_taller(taller_cod: str, db: AsyncSession):
    result = await db.execute(
        select(Emergencia)
        .where(Emergencia.idTaller == taller_cod)
        .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
    )
    return result.scalars().all()
