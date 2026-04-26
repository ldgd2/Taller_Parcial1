from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.mensaje_chat import MensajeChat
from app.models.emergencia import Emergencia
from app.models.taller import Taller
from app.models.tecnico import Tecnico
from app.models.usuario import Usuario
from app.schemas.chat import MensajeChatCreate
from app.core.socket_manager import manager
from fastapi import HTTPException

async def enviar_mensaje(
    emergencia_id: int,
    data: MensajeChatCreate,
    remitente_id: int,
    rol: str,
    db: AsyncSession
):
    # 1. Verificar que la emergencia existe y su estado
    res = await db.execute(
        select(Emergencia)
        .where(Emergencia.id == emergencia_id)
    )
    emergencia = res.scalar_one_or_none()
    
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada")

    if emergencia.idEstado in [7, 8]:
        raise HTTPException(status_code=403, detail="El chat ha finalizado para esta emergencia")

    # 2. Verificar propiedad/permiso del remitente
    if rol == "cliente":
        if emergencia.idCliente != remitente_id:
            raise HTTPException(status_code=403, detail="No tienes permiso para este chat")
    elif rol in ["tecnico", "admin"]:
        if not emergencia.idTaller:
            raise HTTPException(status_code=403, detail="Esta emergencia aún no ha sido asignada a un taller")


        if rol == "tecnico":
            t_check = await db.execute(select(Tecnico).where(Tecnico.id == remitente_id))
            tecnico = t_check.scalar_one_or_none()
            if not tecnico or tecnico.idTaller != emergencia.idTaller:
                raise HTTPException(status_code=403, detail="No perteneces al taller asignado")
        elif rol == "admin":
            a_check = await db.execute(select(Taller).where(Taller.id_admin == remitente_id))
            taller = a_check.scalar_one_or_none()
            if not taller or taller.cod != emergencia.idTaller:
                raise HTTPException(status_code=403, detail="No eres el administrador del taller asignado")

    # 2. Guardar mensaje
    mensaje = MensajeChat(
        idEmergencia=emergencia_id,
        remitente_id=remitente_id,
        rol_remitente=rol,
        contenido=data.contenido,
        imagen_url=data.imagen_url,
        audio_url=data.audio_url
    )
    db.add(mensaje)
    await db.flush()

    # 3. Notificar via WebSocket
    msg_dict = {
        "type": "chat_message",
        "id": mensaje.id,
        "idEmergencia": emergencia_id,
        "remitente_id": remitente_id,
        "rol_remitente": rol,
        "contenido": mensaje.contenido,
        "imagen_url": mensaje.imagen_url,
        "audio_url": mensaje.audio_url,
        "fecha_envio": mensaje.fecha_envio.isoformat()
    }

    # Enviar al cliente
    await manager.send_personal_message(msg_dict, str(emergencia.idCliente))
    
    # Enviar al taller (si está asignado)
    if emergencia.idTaller:
        await manager.send_personal_message(msg_dict, str(emergencia.idTaller))
        
        # También enviar al admin específico por si acaso
        t_res = await db.execute(select(Taller).where(Taller.cod == emergencia.idTaller))
        taller = t_res.scalar_one_or_none()
        if taller and taller.id_admin:
            await manager.send_personal_message(msg_dict, str(taller.id_admin))
    
    if rol != "cliente":
        # --- Notificación Push al Cliente (Móvil) ---

        # --- Notificación Push al Cliente ---
        from app.services.notification_service import NotificationService

        t_res = await db.execute(select(Taller).where(Taller.cod == emergencia.idTaller))
        taller = t_res.scalar_one_or_none()
        nombre_taller = taller.nombre if taller else "Taller Mecánico"
        
        cuerpo = data.contenido if data.contenido else "Foto recibida"
        
        await NotificationService.enviar_notificacion_usuario(
            db=db,
            user_id=emergencia.idCliente,
            titulo=nombre_taller,
            cuerpo=cuerpo,
            data={
                "emergencia_id": emergencia_id,
                "tipo": "chat"
            }
        )

    await db.commit()
    await db.refresh(mensaje)
    return mensaje

async def obtener_historial(emergencia_id: int, db: AsyncSession):
    res = await db.execute(
        select(MensajeChat)
        .where(MensajeChat.idEmergencia == emergencia_id)
        .order_by(MensajeChat.fecha_envio.asc())
    )
    return res.scalars().all()
