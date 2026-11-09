from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.catalogo import Producto
from app.models.inventario import Lote
from app.models.operacion import Inspeccion
from app.models.seguridad import Bodega, Usuario

router = APIRouter(prefix="/inspecciones", tags=["inspecciones"])


class InspeccionVistaRow(BaseModel):
    id: int
    producto_sku: str
    producto_descripcion: str
    numero_lote: str
    bodega_nombre: str
    fecha_inspeccion: datetime
    responsable: str
    cantidad_contada: Decimal | None
    observaciones: str | None


@router.get("/vista", response_model=list[InspeccionVistaRow])
def vista(limit: int = 50, db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            Inspeccion.id,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Bodega.nombre,
            Inspeccion.fecha_inspeccion,
            Usuario.nombre,
            Inspeccion.cantidad_contada,
            Inspeccion.observaciones,
        )
        .join(Lote, Lote.id == Inspeccion.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Bodega, Bodega.id == Inspeccion.bodega_id)
        .join(Usuario, Usuario.id == Inspeccion.responsable_id)
        .order_by(Inspeccion.fecha_inspeccion.desc())
        .limit(limit)
    ).all()
    return [
        InspeccionVistaRow(
            id=r[0],
            producto_sku=r[1],
            producto_descripcion=r[2],
            numero_lote=r[3],
            bodega_nombre=r[4],
            fecha_inspeccion=r[5],
            responsable=r[6],
            cantidad_contada=r[7],
            observaciones=r[8],
        )
        for r in rows
    ]
