from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import entities as crud
from app.models.catalogo import Producto
from app.models.enums import DisposicionNovedad, EstadoAccion
from app.models.inventario import Lote
from app.models.operacion import AccionGestion, Novedad
from app.models.seguridad import Bodega, Usuario
from app.schemas.operacion import GestionRequest

router = APIRouter(prefix="/novedades", tags=["novedades"])


class NovedadVistaRow(BaseModel):
    id: int
    lote_id: int
    producto_sku: str
    producto_descripcion: str
    numero_lote: str
    bodega_nombre: str
    tipo: str
    cantidad_afectada: Decimal
    disposicion: str
    reportado_por: str
    created_at: datetime


class NovedadResumen(BaseModel):
    total: int
    abiertas: int
    cerradas: int
    cantidad_afectada: Decimal
    por_disposicion: dict[str, int]


@router.get("/vista", response_model=list[NovedadVistaRow])
def vista(disposicion: str | None = None, db: Session = Depends(get_db)):
    stmt = (
        select(
            Novedad.id,
            Novedad.lote_id,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Bodega.nombre,
            Novedad.tipo,
            Novedad.cantidad_afectada,
            Novedad.disposicion,
            Usuario.nombre,
            Novedad.created_at,
        )
        .join(Lote, Lote.id == Novedad.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Bodega, Bodega.id == Novedad.bodega_id)
        .join(Usuario, Usuario.id == Novedad.reportado_por_id)
        .order_by(Novedad.created_at.desc())
    )
    if disposicion:
        stmt = stmt.where(Novedad.disposicion == disposicion)
    return [
        NovedadVistaRow(
            id=r[0], lote_id=r[1], producto_sku=r[2], producto_descripcion=r[3],
            numero_lote=r[4], bodega_nombre=r[5], tipo=r[6].value, cantidad_afectada=r[7],
            disposicion=r[8].value, reportado_por=r[9], created_at=r[10],
        )
        for r in db.execute(stmt).all()
    ]


@router.get("/resumen", response_model=NovedadResumen)
def resumen(db: Session = Depends(get_db)):
    por_disp = {
        d.value: c
        for d, c in db.execute(
            select(Novedad.disposicion, func.count()).group_by(Novedad.disposicion)
        ).all()
    }
    total = sum(por_disp.values())
    abiertas = por_disp.get(DisposicionNovedad.pendiente.value, 0)
    total_afectada = db.scalar(select(func.coalesce(func.sum(Novedad.cantidad_afectada), 0)))
    return NovedadResumen(
        total=total,
        abiertas=abiertas,
        cerradas=total - abiertas,
        cantidad_afectada=total_afectada or Decimal(0),
        por_disposicion={d.value: por_disp.get(d.value, 0) for d in DisposicionNovedad},
    )


@router.post("/{item_id}/gestion")
def gestionar(item_id: int, payload: GestionRequest, db: Session = Depends(get_db)) -> dict:
    nov = crud.novedad.get(db, item_id)
    if nov is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Novedad no encontrada")
    if payload.cerrar and not (payload.resultado and payload.resultado.strip()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "El resultado es obligatorio al cerrar la gestion"
        )
    accion = AccionGestion(
        novedad_id=nov.id,
        responsable_id=payload.responsable_id,
        descripcion=payload.descripcion,
        estado=EstadoAccion.cerrada if payload.cerrar else EstadoAccion.abierta,
        resultado=payload.resultado,
        cerrada_en=datetime.now(timezone.utc) if payload.cerrar else None,
    )
    db.add(accion)
    db.commit()
    return {"ok": True, "novedad_id": nov.id, "cerrada": payload.cerrar}
