"""Registro de corta fecha.

Captura en un solo paso lo que el encargado anota recorriendo los pasillos:
codigo (sku), nombre (descripcion), unidades, fecha de vencimiento y lote.

A diferencia de /inspecciones (que exige un lote ya cargado), este endpoint
crea el producto y el lote si no existen, y deja todo listo para el proceso
de alertas: upsert de producto -> lote -> existencia -> inspeccion.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.catalogo import Producto, Proveedor
from app.models.inventario import InventarioLote, Lote
from app.models.operacion import Inspeccion
from app.models.seguridad import Bodega, Usuario

router = APIRouter(prefix="/registros-corta-fecha", tags=["registros-corta-fecha"])


class RegistroCortaFechaCreate(BaseModel):
    sku: str = Field(min_length=1, description="Codigo del producto")
    descripcion: str = Field(min_length=1, description="Nombre del producto")
    numero_lote: str = Field(min_length=1)
    fecha_vencimiento: date
    unidades: Decimal = Field(gt=0)
    bodega_id: int
    proveedor_id: int | None = None
    observaciones: str | None = None


class RegistroVistaRow(BaseModel):
    id: int
    proveedor: str | None
    producto_sku: str
    producto_descripcion: str
    numero_lote: str
    unidades: Decimal | None
    fecha_vencimiento: date | None
    bodega_nombre: str
    responsable: str
    registrado_en: datetime


def _vista_row(db: Session, inspeccion_id: int) -> RegistroVistaRow:
    r = db.execute(
        select(
            Inspeccion.id,
            Proveedor.nombre,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Inspeccion.cantidad_contada,
            Lote.fecha_vencimiento,
            Bodega.nombre,
            Usuario.nombre,
            Inspeccion.fecha_inspeccion,
        )
        .join(Lote, Lote.id == Inspeccion.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .outerjoin(Proveedor, Proveedor.id == Producto.proveedor_id)
        .join(Bodega, Bodega.id == Inspeccion.bodega_id)
        .join(Usuario, Usuario.id == Inspeccion.responsable_id)
        .where(Inspeccion.id == inspeccion_id)
    ).one()
    return RegistroVistaRow(
        id=r[0],
        proveedor=r[1],
        producto_sku=r[2],
        producto_descripcion=r[3],
        numero_lote=r[4],
        unidades=r[5],
        fecha_vencimiento=r[6],
        bodega_nombre=r[7],
        responsable=r[8],
        registrado_en=r[9],
    )


@router.get("/vista", response_model=list[RegistroVistaRow])
def vista(limit: int = 100, db: Session = Depends(get_db)):
    ids = db.scalars(
        select(Inspeccion.id)
        .order_by(Inspeccion.fecha_inspeccion.desc())
        .limit(limit)
    ).all()
    return [_vista_row(db, i) for i in ids]


@router.post("", response_model=RegistroVistaRow, status_code=status.HTTP_201_CREATED)
def crear(
    payload: RegistroCortaFechaCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    bodega = db.get(Bodega, payload.bodega_id)
    if bodega is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Bodega no encontrada")
    if payload.proveedor_id is not None and db.get(Proveedor, payload.proveedor_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Proveedor no encontrado")

    sku = payload.sku.strip()
    numero_lote = payload.numero_lote.strip()

    # 1. Producto: buscar por sku, crear si no existe.
    producto = db.scalar(select(Producto).where(Producto.sku == sku))
    if producto is None:
        producto = Producto(
            sku=sku,
            descripcion=payload.descripcion.strip(),
            proveedor_id=payload.proveedor_id,
        )
        db.add(producto)
        db.flush()
    elif payload.proveedor_id is not None and producto.proveedor_id is None:
        producto.proveedor_id = payload.proveedor_id

    # 2. Lote: buscar por (producto, numero_lote), crear si no existe.
    lote = db.scalar(
        select(Lote).where(
            Lote.producto_id == producto.id, Lote.numero_lote == numero_lote
        )
    )
    if lote is None:
        lote = Lote(
            producto_id=producto.id,
            numero_lote=numero_lote,
            fecha_vencimiento=payload.fecha_vencimiento,
        )
        db.add(lote)
        db.flush()
    elif lote.fecha_vencimiento != payload.fecha_vencimiento:
        lote.fecha_vencimiento = payload.fecha_vencimiento

    # 3. Existencia por bodega: snapshot de lo contado fisicamente.
    inv = db.scalar(
        select(InventarioLote).where(
            InventarioLote.lote_id == lote.id,
            InventarioLote.bodega_id == payload.bodega_id,
        )
    )
    if inv is None:
        db.add(
            InventarioLote(
                lote_id=lote.id,
                bodega_id=payload.bodega_id,
                cantidad=payload.unidades,
            )
        )
    else:
        inv.cantidad = payload.unidades

    # 4. Inspeccion: la captura fisica confirmada por el responsable.
    insp = Inspeccion(
        lote_id=lote.id,
        bodega_id=payload.bodega_id,
        responsable_id=user.id,
        cantidad_contada=payload.unidades,
        fecha_vencimiento_verificada=payload.fecha_vencimiento,
        observaciones=payload.observaciones,
    )
    db.add(insp)
    db.commit()
    db.refresh(insp)
    return _vista_row(db, insp.id)
