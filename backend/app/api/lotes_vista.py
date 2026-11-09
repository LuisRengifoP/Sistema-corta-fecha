from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.lotes_vista import LoteDetalle, LoteVistaRow
from app.services import lotes as svc

# Prefijo /lotes; se incluye ANTES del CRUD generico para que /vista y
# /{id}/detalle tengan prioridad sobre la ruta /{item_id}.
router = APIRouter(prefix="/lotes", tags=["lotes"])


@router.get("/vista", response_model=list[LoteVistaRow])
def vista(
    q: str | None = None,
    estado: str | None = None,
    sucursal_id: int | None = None,
    sin_fecha: bool = False,
    db: Session = Depends(get_db),
):
    return svc.listar_vista(
        db, q=q, estado=estado, sucursal_id=sucursal_id, sin_fecha=sin_fecha
    )


@router.get("/{lote_id}/detalle", response_model=LoteDetalle)
def detalle(lote_id: int, db: Session = Depends(get_db)):
    d = svc.detalle(db, lote_id)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lote no encontrado")
    return d
