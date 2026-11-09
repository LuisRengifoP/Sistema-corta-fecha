from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.catalogo import Producto
from app.models.enums import EstadoAlerta, EstadoSeguimiento
from app.models.inventario import Lote
from app.models.operacion import Alerta

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/resumen")
def resumen(db: Session = Depends(get_db)) -> dict:
    """Indicadores para el dashboard: alertas por estado y por seguimiento."""
    por_estado = dict(
        db.execute(
            select(Alerta.estado, func.count()).group_by(Alerta.estado)
        ).all()
    )
    por_seguimiento = dict(
        db.execute(
            select(Alerta.seguimiento, func.count()).group_by(Alerta.seguimiento)
        ).all()
    )

    estados = {s.value: por_estado.get(s, 0) for s in EstadoAlerta}
    seguimientos = {s.value: por_seguimiento.get(s, 0) for s in EstadoSeguimiento}

    total_productos = db.scalar(select(func.count()).select_from(Producto)) or 0
    total_lotes = db.scalar(select(func.count()).select_from(Lote)) or 0
    lotes_sin_fecha = (
        db.scalar(
            select(func.count())
            .select_from(Lote)
            .where(Lote.fecha_vencimiento.is_(None), Lote.activo.is_(True))
        )
        or 0
    )
    total_alertas = sum(estados.values())

    return {
        "alertas_por_estado": estados,
        "alertas_por_seguimiento": seguimientos,
        "total_alertas": total_alertas,
        "total_productos": total_productos,
        "total_lotes": total_lotes,
        "lotes_sin_fecha": lotes_sin_fecha,
    }
