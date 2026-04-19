"""
Router de Pagos — CU05
POST /pagos/{emergencia_id}  → Registrar pago de una emergencia finalizada
GET  /pagos/{emergencia_id}  → Obtener pago de una emergencia
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

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post(
    "/{emergencia_id}",
    response_model=PagoOut,
    summary="CU05 — Registrar pago de emergencia atendida",
)
async def registrar_pago(
    emergencia_id: int,
    data: PagoCreate,
    current=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Registra el pago de una emergencia que fue atendida.
    Solo admins del taller pueden registrar pagos.
    """
    # Verificar que la emergencia existe
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia:
        raise HTTPException(status_code=404, detail="Emergencia no encontrada.")

    # Verificar que pertenece al taller del admin
    taller_cod = current.get("taller")
    if emergencia.idTaller != taller_cod:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta emergencia no pertenece a tu taller."
        )

    # Calcular comisión (10%)
    comision = data.monto * Decimal("0.10")

    pago = Pago(
        monto=data.monto,
        monto_comision=comision,
        fecha_pago=datetime.date.today(),
    )
    db.add(pago)
    await db.flush()

    # Vincular pago a la emergencia
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
    res = await db.execute(select(Emergencia).where(Emergencia.id == emergencia_id))
    emergencia = res.scalar_one_or_none()
    if not emergencia or not emergencia.idPago:
        raise HTTPException(status_code=404, detail="Pago no encontrado para esta emergencia.")

    pago_res = await db.execute(select(Pago).where(Pago.id == emergencia.idPago))
    return pago_res.scalar_one()
