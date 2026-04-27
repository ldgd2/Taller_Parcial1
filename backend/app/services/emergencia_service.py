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
from app.core.config import settings
from app.services.ai_service import analizar_transcripcion_whisper
from typing import List
import math
from app.services.notification_service import NotificationService


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

    # CU08, CU09, CU10: IA processing si hay texto o imágenes
    print(f"Evaluando IA: texto={bool(data.texto_adicional)}, fotos={len(data.evidencias_urls)}")
    if data.texto_adicional or data.evidencias_urls:
        try:
            # Obtener catálogos para el prompt de IA
            cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.descripcion))
            prios_res = await db.execute(select(Prioridad.id, Prioridad.descripcion))
            
            categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in cats_res.all()]
            prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prios_res.all()]

            # Construir URLs completas
            # Si el path ya empieza con uploads/, no lo duplicamos
            base_url_simple = f"http://{settings.APP_HOST}:8000"
            full_urls = []
            for u in data.evidencias_urls:
                if u.startswith('http'):
                    full_urls.append(u)
                elif u.startswith('uploads/'):
                    full_urls.append(f"{base_url_simple}/{u}")
                else:
                    full_urls.append(f"{base_url_simple}/uploads/{u}")

            print(f"🖼️ URLs enviadas a IA: {full_urls}")

            # Llamada al servicio de IA OpenRouter + Instructor (Multi-modal)
            ia_result = await analizar_transcripcion_whisper(
                texto_crudo=data.texto_adicional or "Sin descripción (ver fotos)",
                vehiculo_info=vehiculo_contexto,
                categorias_disponibles=categorias_activas,
                prioridades_disponibles=prioridades_activas,
                evidencias_urls=full_urls
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
        audio_url=data.audio_url,
        es_valida=True if not data.texto_adicional else True # Se actualizará abajo si la IA lo dice
    )
    db.add(emergencia)
    await db.flush()

    # CU05: Crear pago inicial en 0 para evitar nulos (Modo Failsafe)
    from app.models.pago import Pago
    pago_inicial = Pago(
        monto=0,
        monto_comision=0,
        cliente_id=cliente_id,
        emergencia_id=emergencia.id,
        estado="PENDIENTE"
    )
    db.add(pago_inicial)
    await db.flush()

    # Guardar Evidencias (Fotos)
    from app.models.evidencia import Evidencia
    for url in data.evidencias_urls:
        evidencia = Evidencia(
            direccion=url,
            idEmergencia=emergencia.id
        )
        db.add(evidencia)
    await db.flush()

    # Guardar análisis IA si fue procesado
    if resumen_taller:
        resumen_ia = ResumenIA(
            resumen=resumen_taller,
            ficha_tecnica=ficha_tecnica,
            recomendaciones_taller=ia_result.recomendaciones_taller if 'ia_result' in locals() else None,
            motivo_rechazo=ia_result.motivo_rechazo if 'ia_result' in locals() else None,
            idEmergencia=emergencia.id
        )
        db.add(resumen_ia)
        if 'ia_result' in locals():
            emergencia.es_valida = ia_result.es_valida
            
            if not ia_result.es_valida:
                try:
                    from app.services.chat_service import enviar_notificacion_push
                    await enviar_notificacion_push(
                        user_id=cliente.idUsuario,
                        title="Reporte Requiere Corrección",
                        body=f"La IA no pudo validar tu reporte: {ia_result.motivo_rechazo}. Por favor, corrige los datos o cancela.",
                        data={
                            "tipo": "emergencia_invalida",
                            "emergencia_id": str(emergencia.id),
                            "motivo": ia_result.motivo_rechazo
                        }
                    )
                except Exception as e:
                    print(f"Error enviando notificacion de rechazo IA: {e}")
        
        await db.flush()


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
            joinedload(Emergencia.vehiculo),
            selectinload(Emergencia.pago)
        )
        .where(Emergencia.id == id)
    )
    res = await db.execute(stmt)
    emergencia = res.unique().scalar_one_or_none()
    if emergencia:
        _populate_dynamic_fields(emergencia)
    return emergencia

def _populate_dynamic_fields(e: Emergencia):
    """Calcula campos que no estn en la tabla base para el esquema de salida."""
    if e.historial:
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
            joinedload(Emergencia.vehiculo),
            joinedload(Emergencia.pago)
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

    # NOTIFICACIÓN AL CLIENTE (CU12)
    try:
        # Obtener nombre del nuevo estado para el mensaje
        estado_nombre = (await db.execute(select(Estado.nombre).where(Estado.id == data.idEstado))).scalar()
        await NotificationService.enviar_notificacion_usuario(
            db, 
            emergencia.idCliente, 
            "Actualización de Servicio", 
            f"Tu reporte '{emergencia.descripcion}' ahora está: {estado_nombre}",
            {"emergencia_id": str(emergencia_id), "tipo": "estado_change"}
        )
    except Exception as e:
        print(f"Error al enviar notificación: {e}")

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
            joinedload(Emergencia.vehiculo),
            joinedload(Emergencia.pago)
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
            joinedload(Emergencia.vehiculo),
            joinedload(Emergencia.pago)
        )
        .where(Emergencia.idTaller.is_(None))
        .where(Emergencia.idEstado.in_(estados_validos)) 
        .where(Emergencia.es_valida.is_(True)) # FILTRO DE CONTEXTO
        .where(CategoriaProblema.idEspecialidad.in_(especialidades_taller))
    )
    
    emergencias_res = await db.execute(stmt)
    todas_disponibles = emergencias_res.scalars().all()

    # 4. Filtrar por distancia (10km)
    cercanas = []
    for e in todas_disponibles:
        dist = haversine_distance(taller.latitud, taller.longitud, e.latitud, e.longitud)
        if dist <= 10: # Radio de 10km
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
    """Asignación final con uno o varios técnicos."""
    # 1. Obtener emergencia
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
    
    if emergencia.idTaller and emergencia.idTaller != taller_cod:
        raise HTTPException(status_code=400, detail="Esta emergencia ya fue tomada por otro taller.")

    # 2. Realizar asignación
    emergencia.idTaller = taller_cod
    emergencia.locked_by = None
    emergencia.locked_at = None
    
    # 3. Registrar técnicos
    from app.models.asignacion_tecnico_emergencia import AsignacionTecnicoEmergencia
    await db.execute(
        AsignacionTecnicoEmergencia.__table__.delete().where(
            AsignacionTecnicoEmergencia.idEmergencia == emergencia_id
        )
    )

    for t_id in tecnicos_ids:
        asig = AsignacionTecnicoEmergencia(idEmergencia=emergencia_id, idTecnico=t_id)
        db.add(asig)
    
    # 4. Actualizar estado a 'ASIGNADO'
    estado_res = await db.execute(select(Estado).where(Estado.nombre == "ASIGNADO"))
    estado = estado_res.scalar_one_or_none()
    
    emergencia.idEstado = estado.id if estado else 2
    historial = HistorialEstado(
        idEmergencia=emergencia_id,
        idEstado=emergencia.idEstado,
    )
    db.add(historial)
        
    await db.commit()
    # Refrescamos para tener los datos del objeto actualizados tras el commit
    await db.refresh(emergencia)

    # 5. NOTIFICACIÓN AL CLIENTE (CU12)
    try:
        taller_res = await db.execute(select(Taller).where(Taller.cod == taller_cod))
        taller = taller_res.scalar_one_or_none()
        
        # Calcular distancia y tiempo estimado
        distancia = haversine_distance(taller.latitud, taller.longitud, emergencia.latitud, emergencia.longitud)
        tiempo_estimado = round(distancia * 2.5 + 5)
        dist_str = f"{distancia:.1f} km"
        
        print(f"DEBUG: Intentando enviar notificación a Cliente {emergencia.idCliente}")
        
        await NotificationService.enviar_notificacion_usuario(
            db, 
            emergencia.idCliente, 
            "¡Ayuda en camino! 🛠️", 
            f"El taller '{taller.nombre}' ha aceptado tu solicitud. Está a {dist_str} y llegará en aprox. {tiempo_estimado} min. ¡Mantén la calma!",
            {
                "emergencia_id": str(emergencia_id), 
                "tipo": "taller_asignado",
                "distancia": dist_str,
                "tiempo": str(tiempo_estimado)
            }
        )
    except Exception as e:
        print(f"Error al enviar notificación de asignación: {e}")

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


async def finalizar_emergencia(
    emergencia_id: int,
    data: dict, # Usando dict o schema
    taller_cod: str,
    db: AsyncSession
):
    """
    Finaliza el servicio, crea el registro de pago y notifica al cliente.
    """
    from app.models.pago import Pago
    
    try:
        # 1. Validar emergencia
        stmt = (
            select(Emergencia)
            .where(Emergencia.id == emergencia_id)
            .options(selectinload(Emergencia.pago))
        )
        res = await db.execute(stmt)
        emergencia = res.unique().scalar_one_or_none()
        
        if not emergencia:
            raise HTTPException(status_code=404, detail="Emergencia no encontrada.")
            
        if emergencia.idTaller != taller_cod:
            print(f"DEBUG 403: e.idTaller={emergencia.idTaller}, user.taller={taller_cod}")
            raise HTTPException(status_code=403, detail="No tienes acceso a esta emergencia.")

        # 2. Actualizar o Crear Pago
        factura = data.get("factura", None)
        
        if factura and isinstance(factura, dict):
            monto_raw = factura.get("total_general", data.get("monto_total", 0))
        else:
            monto_raw = data.get("monto_total", 0)
            
        try:
            monto = float(monto_raw)
        except:
            monto = 0.0
            
        comision = monto * 0.10
        
        # Log para depuración de IntegrityError
        print(f"DEBUG PAGOS: idCliente={emergencia.idCliente}, idEmergencia={emergencia_id}, monto={monto}")
        
        if emergencia.pago:
            pago = emergencia.pago
            pago.monto = monto
            pago.monto_comision = comision
            pago.estado = "PENDIENTE" # Sigue pendiente hasta que el cliente pague
            pago.detalle_factura = factura
        else:
            # Aseguramos que los IDs no sean nulos
            c_id = emergencia.idCliente
            e_id = emergencia_id
            
            if c_id is None or e_id is None:
                print(f"ERROR: No se puede crear pago con IDs nulos. c_id={c_id}, e_id={e_id}")
                raise HTTPException(status_code=500, detail="Error de integridad: Datos de cliente o emergencia faltantes.")

            nuevo_pago = Pago(
                monto=monto,
                monto_comision=comision,
                cliente_id=c_id,
                emergencia_id=e_id,
                estado="PENDIENTE",
                detalle_factura=factura
            )
            db.add(nuevo_pago)
            await db.flush()
        
        # Cambiar a estado ATENDIDO (ID 6 según check_states.py)
        emergencia.idEstado = 6
        historial = HistorialEstado(
            idEmergencia=emergencia_id,
            idEstado=6,
        )
        db.add(historial)
        
        await db.commit()
        
        # 4. Notificar al Cliente
        try:
            await NotificationService.enviar_notificacion_usuario(
                db,
                emergencia.idCliente,
                "¡Trabajo Terminado! ✅",
                f"El taller ha finalizado el servicio. El monto total a pagar es: ${monto:.2f}. Por favor, procede al pago.",
                {
                    "emergencia_id": str(emergencia_id),
                    "tipo": "pago_pendiente",
                    "monto": str(monto)
                }
            )
        except Exception as e:
            print(f"Error enviando notificación de finalización: {e}")

        return {
            "status": "ok", 
            "message": "Emergencia finalizada y cliente notificado.",
            "monto_total": monto,
            "monto_comision": comision,
            "monto_taller": monto - comision
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = f"Error en finalizar_emergencia: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        with open("error_log.txt", "a") as f:
            f.write("\n" + "="*50 + "\n" + error_msg + "\n")
        raise HTTPException(status_code=500, detail="Error interno del servidor al finalizar.")
async def actualizar_emergencia(id_emergencia: int, data: EmergenciaCreate, user_id: int, db: AsyncSession):
    # 1. Verificar propiedad y estado
    res = await db.execute(select(Emergencia).where(Emergencia.id == id_emergencia))
    emergencia = res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    # Solo el dueño puede editar
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para editar esta emergencia")

    # Solo se puede editar si no ha sido aceptada (idEstado de PENDIENTE)
    estado_pend_res = await db.execute(select(Estado).where(Estado.nombre == "PENDIENTE"))
    estado_pend = estado_pend_res.scalar_one()
    if emergencia.idEstado != estado_pend.id:
        raise HTTPException(status_code=400, detail="No se puede editar una emergencia que ya está siendo atendida")

    # 2. Actualizar datos básicos
    emergencia.descripcion = data.descripcion
    emergencia.latitud = data.latitud
    emergencia.longitud = data.longitud
    emergencia.direccion = data.direccion
    emergencia.audio_url = data.audio_url
    
    # 3. Re-procesar IA si hay texto o imágenes
    print(f"🔍 [Update] Evaluando IA: texto={bool(data.texto_adicional)}, fotos={len(data.evidencias_urls)}")
    if data.texto_adicional or data.evidencias_urls:
        from app.services.ai_service import analizar_transcripcion_whisper
        from app.core.config import settings

        # Contexto del vehículo
        veh_res = await db.execute(select(Vehiculo).where(Vehiculo.placa == data.placaVehiculo))
        veh = veh_res.scalar_one_or_none()
        vehiculo_contexto = f"{veh.marca} {veh.modelo} ({veh.anio})" if veh else ""

        # Categorías y Prioridades activas
        cats_res = await db.execute(select(CategoriaProblema.id, CategoriaProblema.descripcion))
        prios_res = await db.execute(select(Prioridad.id, Prioridad.descripcion))
        categorias_activas = [{"id": r.id, "nombre": r.descripcion} for r in cats_res.all()]
        prioridades_activas = [{"id": r.id, "nombre": r.descripcion} for r in prios_res.all()]

        # Construir URLs completas
        base_url_simple = f"http://{settings.APP_HOST}:8000"
        full_urls = []
        for u in data.evidencias_urls:
            if u.startswith('http'):
                full_urls.append(u)
            elif u.startswith('uploads/'):
                full_urls.append(f"{base_url_simple}/{u}")
            else:
                full_urls.append(f"{base_url_simple}/uploads/{u}")

        print(f"🖼️ [Update] URLs enviadas a IA: {full_urls}")
        
        ia_result = await analizar_transcripcion_whisper(
            texto_crudo=data.texto_adicional or data.descripcion or "Sin descripción",
            vehiculo_info=vehiculo_contexto,
            categorias_disponibles=categorias_activas,
            prioridades_disponibles=prioridades_activas,
            evidencias_urls=full_urls
        )

        # 4. Actualizar Resumen IA
        resumen_res = await db.execute(select(ResumenIA).where(ResumenIA.idEmergencia == id_emergencia))
        resumen_ia = resumen_res.scalar_one_or_none()
        
        ficha_tecnica = ia_result.ficha_tecnica.model_dump() if ia_result.ficha_tecnica else {}
        resumen_taller = ia_result.resumen_taller

        if resumen_ia:
            resumen_ia.resumen = resumen_taller
            resumen_ia.ficha_tecnica = ficha_tecnica
            resumen_ia.recomendaciones_taller = ia_result.recomendaciones_taller
            resumen_ia.motivo_rechazo = ia_result.motivo_rechazo
        else:
            resumen_ia = ResumenIA(
                resumen=resumen_taller,
                ficha_tecnica=ficha_tecnica,
                recomendaciones_taller=ia_result.recomendaciones_taller,
                motivo_rechazo=ia_result.motivo_rechazo,
                idEmergencia=emergencia.id
            )
            db.add(resumen_ia)

        # Actualizar flags y clasificación
        emergencia.es_valida = ia_result.es_valida
        emergencia.idCategoria = ia_result.id_categoria
        emergencia.idPrioridad = ia_result.id_prioridad 

    # 5. Actualizar Evidencias (Borrar antiguas y poner nuevas)
    from app.models.evidencia import Evidencia
    from sqlalchemy import delete
    await db.execute(delete(Evidencia).where(Evidencia.idEmergencia == id_emergencia))
    
    for url in data.evidencias_urls:
        evidencia = Evidencia(direccion=url, idEmergencia=id_emergencia)
        db.add(evidencia)

    await db.commit()
    await db.refresh(emergencia)
    return emergencia

async def cancelar_emergencia(id_emergencia: int, user_id: int, db: AsyncSession):
    res = await db.execute(
        select(Emergencia).where(Emergencia.id == id_emergencia)
    )
    emergencia = res.scalar_one_or_none()
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    if emergencia.idCliente != user_id:
         raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta emergencia")

    if emergencia.idTaller is not None:
        raise HTTPException(
            status_code=400, 
            detail="No se puede eliminar una emergencia que ya ha sido aceptada por un taller. Intente contactar con soporte."
        )

    await db.delete(emergencia)
    await db.commit()
    
    return {"status": "success", "message": "Emergencia eliminada permanentemente"}
async def obtener_emergencia_por_id(emergencia_id: int, db: AsyncSession) -> Emergencia:
    stmt = (
        select(Emergencia)
        .options(
            selectinload(Emergencia.resumen_ia),
            selectinload(Emergencia.evidencias),
            selectinload(Emergencia.tecnicos_asignados).selectinload(Tecnico.especialidades),
            selectinload(Emergencia.historial).joinedload(HistorialEstado.estado),
            joinedload(Emergencia.vehiculo),
            joinedload(Emergencia.estado),
            selectinload(Emergencia.pago)
        )
        .where(Emergencia.id == emergencia_id)
    )
    result = await db.execute(stmt)
    emergencia = result.unique().scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")
    
    _populate_dynamic_fields(emergencia)
    return emergencia
