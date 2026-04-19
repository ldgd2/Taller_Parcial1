"""
CU05 — Gestionar Tipo de Pago

POST /pagos/{emergencia_id} → Registrar pago de una emergencia finalizada
GET  /pagos/{emergencia_id} → Obtener pago registrado de una emergencia

Regla de negocio:
  - Comisión de plataforma: 10% del monto total del servicio
  - Solo admins del taller al que pertenece la emergencia pueden registrar el pago
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
import datetime

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.pago import Pago
from app.models.emergencia import Emergencia
from app.schemas.pago import PagoCreate, PagoOut

router = APIRouter(prefix="/pagos", tags=["Comercio — Pagos (CU05)"])


@router.post(
    "/{emergencia_id}",
    response_model=PagoOut,
    status_code=201,
    summary="CU05 — Registrar pago de emergencia atendida",
)
async def registrar_pago(
    emergencia_id: int,
    data: PagoCreate,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    CU05: Registra el pago del servicio de emergencia.
    Calcula automáticamente la comisión del 10% y el monto neto al taller.
    Solo el admin del taller propietario puede registrar el pago.
    """
    # 1. Verificar que la emergencia existe
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")

    # 2. Verificar que pertenece al taller del admin autenticado
    taller_cod = current.get("taller")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta emergencia no pertenece a tu taller.",
        )

    # 3. Calcular comisión de plataforma (10%)
    comision = data.monto * Decimal("0.10")

    pago = Pago(
        monto=data.monto,
        monto_comision=comision,
        fecha_pago=datetime.date.today(),
    )
    db.add(pago)
    await db.flush()

    # 4. Vincular pago a la emergencia
    emergencia.idPago = pago.id
    await db.commit()
    await db.refresh(pago)
    return pago


@router.get(
    "/{emergencia_id}",
    response_model=PagoOut,
    summary="CU05 — Obtener pago de una emergencia",
)
async def obtener_pago(
    emergencia_id: int,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """Retorna el registro de pago asociado a la emergencia, si existe."""
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia or not emergencia.idPago:
        raise HTTPException(status_code=404, detail="Pago no encontrado para esta emergencia.")

    pago_res = await db.execute(select(Pago).where(Pago.id == emergencia.idPago))
    return pago_res.scalar_one()
