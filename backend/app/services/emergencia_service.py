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
from app.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia
from app.models.categoria_problema import CategoriaProblema
from app.models.resumen_ia import ResumenIA
from app.models.taller import Taller
from app.models.tecnico import Tecnico
from app.models.asignacion_especialidad import AsignacionEspecialidad
from app.schemas.emergencia import EmergenciaCreate, EmergenciaOut, ActualizarEstadoRequest
from sqlalchemy.orm import selectinload, joinedload
from app.services.ai_service import analizar_transcripcion_whisper
from typing import List
import math


# ─── CU04 ─────────────────────────────────────────────────────────

async def reportar_emergencia(
    data: EmergenciaCreate,
    cliente_id: int,
    db: AsyncSession,
) -> EmergenciaOut:
    # Validar que el vehículo pertenece al cliente y obtener datos para la IA
    res = await db.execute(
        select(Vehiculo).where(
            Vehiculo.placa == data.placaVehiculo,
            Vehiculo.idCliente == cliente_id,
        )
    )
    vehiculo = res.scalar_one_or_none()
    if vehiculo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehículo no encontrado o no pertenece al cliente.",
        )

    # Contexto del vehículo para la IA
    vehiculo_contexto = f"{vehiculo.marca} {vehiculo.modelo} {vehiculo.anio} (Placa: {vehiculo.placa})"

    # Valores por defecto para el reporte inicial (CU11 - Desacoplado)
    # Estos valores pueden ser sobrescritos por el análisis de IA más adelante.
    prioridad_id = 1  # BAJA por defecto
    categoria_id = 5  # OTROS por defecto (ajustar según seed)
    resumen_taller = ""
    ficha_tecnica = None

    # CU08, CU09, CU10: IA processing si hay texto
    if data.texto_adicional:
        try:
            # Obtener catálogos para el prompt de IA
            cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.descripcion))
            prios_res = await db.execute(select(Prioridad.id, Prioridad.descripcion))
            
            categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in cats_res.all()]
            prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prios_res.all()]

            # Llamada al servicio de IA OpenRouter + Instructor
            ia_result = await analizar_transcripcion_whisper(
                texto_crudo=data.texto_adicional,
                vehiculo_info=vehiculo_contexto,
                categorias_disponibles=categorias_activas,
                prioridades_disponibles=prioridades_activas
            )

            # Reemplazar valores base con los dictaminados por la IA
            prioridad_id = ia_result.id_prioridad
            categoria_id = ia_result.id_categoria
            resumen_taller = ia_result.resumen_taller
            # Usar el título generado por la IA en lugar de la descripción del usuario
            if ia_result.titulo_emergencia:
                data.descripcion = ia_result.titulo_emergencia
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
        idTaller=None,
        idPrioridad=prioridad_id,
        idCategoria=categoria_id,
        idCliente=cliente_id,
        placaVehiculo=data.placaVehiculo,
        audio_url=data.audio_url
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

    # Registrar estado inicial -> PENDIENTE
    estado_res = await db.execute(select(Estado).where(Estado.nombre == "PENDIENTE"))
    estado = estado_res.scalar_one_or_none()
    if estado is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Estado 'PENDIENTE' no encontrado en BD. Ejecute el seed inicial.",
        )

    emergencia.idEstado = estado.id
    historial = HistorialEstado(
        idEmergencia=emergencia.id,
        idEstado=estado.id,
    )
    db.add(historial)
    await db.commit()

    return await obtener_emergencia_detalle(emergencia.id, db)

async def obtener_emergencia_detalle(id: int, db: AsyncSession):
    stmt = (
        select(Emergencia)
        .options(
            selectinload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo)
        )
        .where(Emergencia.id == id)
    )
    res = await db.execute(stmt)
    emergencia = res.scalar_one_or_none()
    if emergencia:
        _populate_dynamic_fields(emergencia)
    return emergencia

def _populate_dynamic_fields(e: Emergencia):
    """Calcula campos que no estn en la tabla base para el esquema de salida."""
    # 1. Estado Actual
    if e.historial:
        # El ms reciente por fechaCambio o por ID si las fechas son iguales
        last_h = sorted(e.historial, key=lambda x: (x.fecha_cambio, x.id), reverse=True)[0]
        e.estado_actual = last_h.estado.nombre
    else:
        e.estado_actual = "DESCONOCIDO"

    # 2. Mutex (is_locked)
    e.is_locked = False
    if e.locked_by and e.locked_at:
        diff = datetime.datetime.now() - e.locked_at
        if diff.total_seconds() < 120:
            e.is_locked = True


# ─── CU14 (cliente consulta sus emergencias) ──────────────────────

async def listar_emergencias_cliente(cliente_id: int, db: AsyncSession):
    stmt = (
        select(Emergencia)
        .options(
            selectinload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo)
        )
        .where(Emergencia.idCliente == cliente_id)
        .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
    )
    result = await db.execute(stmt)
    emergencias = result.scalars().all()
    for e in emergencias:
        _populate_dynamic_fields(e)
    return emergencias


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

    emergencia.idEstado = data.idEstado
    nuevo_historial = HistorialEstado(
        idEmergencia=emergencia_id,
        idEstado=data.idEstado,
    )
    db.add(nuevo_historial)
    await db.flush()
    return nuevo_historial


# CU15 (taller actualiza el estado de la emergencia) ──────────

async def listar_emergencias_taller(taller_cod: str, db: AsyncSession):
    stmt = (
        select(Emergencia)
        .options(
            joinedload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo)
        )
        .where(Emergencia.idTaller == taller_cod)
        .order_by(desc(Emergencia.fecha), desc(Emergencia.hora))
    )
    result = await db.execute(stmt)
    emergencias = result.scalars().all()
    for e in emergencias:
        _populate_dynamic_fields(e)
    return emergencias


# ─── GESTIÓN DE TABLERO DE EMERGENCIAS (Admin Workshops) ──────────

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en KM entre dos puntos usando la fórmula de Haversine."""
    if not all([lat1, lon1, lat2, lon2]): return 999999
    R = 6371  # Radio de la Tierra en km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c

async def listar_emergencias_disponibles(taller_cod: str, db: AsyncSession):
    """
    Lista emergencias que:
    1. No tienen taller asignado (idTaller IS NULL)
    2. El taller tiene la especialidad requerida por la categoria de la emergencia
    3. Están dentro de un radio de 50km
    """
    # 1. Obtener datos del taller
    taller_res = await db.execute(select(Taller).where(Taller.cod == taller_cod))
    taller = taller_res.scalar_one_or_none()
    if not taller: return []

    # 2. Obtener especialidades del taller
    esp_res = await db.execute(
        select(AsignacionEspecialidad.idEspecialidad).where(AsignacionEspecialidad.idTaller == taller_cod)
    )
    especialidades_taller = [r[0] for r in esp_res.all()]

    # 3. Buscar emergencias sin taller asignado y en estado PENDIENTE / INICIADA
    # Filtramos por especialidad requerida (match entre taller y categoria)
    estados_validos_res = await db.execute(select(Estado.id).where(Estado.nombre.in_(["INICIADA", "PENDIENTE"])))
    estados_validos = [r[0] for r in estados_validos_res.all()]
    if not estados_validos:
        estados_validos = [1, 2] # Fallback
        
    stmt = (
        select(Emergencia)
        .join(CategoriaProblema)
        .options(
            joinedload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo)
        )
        .where(Emergencia.idTaller.is_(None))
        .where(Emergencia.idEstado.in_(estados_validos)) 
        .where(CategoriaProblema.idEspecialidad.in_(especialidades_taller))
    )
    
    emergencias_res = await db.execute(stmt)
    todas_disponibles = emergencias_res.scalars().all()

    # 4. Filtrar por distancia (50km)
    cercanas = []
    for e in todas_disponibles:
        dist = haversine_distance(taller.latitud, taller.longitud, e.latitud, e.longitud)
        if dist <= 50: # Radio de 50km
            _populate_dynamic_fields(e)
            cercanas.append(e)
            
    return cercanas

async def bloquear_emergencia_temporal(emergencia_id: int, taller_cod: str, db: AsyncSession):
    """Establece un mutex temporal de 2 minutos."""
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia or emergencia.idTaller:
        raise HTTPException(status_code=400, detail="Emergencia no disponible para análisis.")
    
    emergencia.locked_by = taller_cod
    emergencia.locked_at = datetime.datetime.now()
    await db.commit()
    return {"status": "locked", "expires_in": 120}

async def asignar_emergencia_taller(emergencia_id: int, taller_cod: str, tecnicos_ids: List[int], db: AsyncSession):
    """Asignación final atómica con uno o varios técnicos."""
    async with db.begin():
        res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
        emergencia = res.scalar_one_or_none()
        
        if not emergencia:
            raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
        
        if emergencia.idTaller and emergencia.idTaller != taller_cod:
            raise HTTPException(status_code=400, detail="Esta emergencia ya fue tomada por otro taller.")

        # Realizar asignación
        emergencia.idTaller = taller_cod
        emergencia.locked_by = None
        emergencia.locked_at = None
        
        # Registrar múltiples técnicos
        # Primero limpiamos si hubiera algo (por re-asignacion del mismo taller)
        from app.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia
        await db.execute(
            AsignacionTecnicoEmergencia.__table__.delete().where(
                AsignacionTecnicoEmergencia.idEmergencia == emergencia_id
            )
        )

        for t_id in tecnicos_ids:
            asig = AsignacionTecnicoEmergencia(idEmergencia=emergencia_id, idTecnico=t_id)
            db.add(asig)
        
        # Actualizar estado a 'ASIGNADO'
        estado_res = await db.execute(select(Estado).where(Estado.nombre == "ASIGNADO"))
        estado = estado_res.scalar_one_or_none()
        
        emergencia.idEstado = estado.id if estado else 2
        historial = HistorialEstado(
            idEmergencia=emergencia_id,
            idEstado=emergencia.idEstado,
        )
        db.add(historial)
        
    await db.commit()
    return {"status": "ok", "message": f"Emergencia asignada a {len(tecnicos_ids)} técnicos."}


# ─── CU10 — El taller actualiza la ficha técnica con datos reales ──

async def actualizar_ficha_tecnica(emergencia_id: int, data: dict, taller_cod: str, db: AsyncSession):
    """
    CU10: Generación de Ficha Técnica — El taller puede completar/corregir
    el diagnóstico, piezas y acciones con los datos reales del servicio.
    """
    from app.models.resumen_ia import ResumenIA
    
    # Verificar que la emergencia pertenece al taller
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta emergencia.")
    
    # Obtener o crear ResumenIA
    resumen_res = await db.execute(select(ResumenIA).where(ResumenIA.idEmergencia == emergencia_id))
    resumen = resumen_res.scalar_one_or_none()
    
    if resumen:
        # Actualizar ficha técnica existente (merge con datos nuevos)
        existing_ficha = resumen.ficha_tecnica or {}
        existing_ficha.update(data.get("ficha_tecnica", {}))
        resumen.ficha_tecnica = existing_ficha
        if "resumen" in data:
            resumen.resumen = data["resumen"]
    else:
        # Crear resumen si no fue generado por IA
        resumen = ResumenIA(
            resumen=data.get("resumen", "Diagnóstico completado por el taller."),
            ficha_tecnica=data.get("ficha_tecnica", {}),
            idEmergencia=emergencia_id
        )
        db.add(resumen)
    
    await db.commit()
    return {"status": "ok", "message": "Ficha técnica actualizada correctamente."}

