from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.catalogo import Categoria, Producto, Proveedor
from app.models.inventario import InventarioLote, Lote
from app.models.operacion import Inspeccion
from app.models.seguridad import Bodega, Sucursal, Usuario
from app.services.alertas import clasificar, _umbrales_de


def _cajas_unidades(total: Decimal, factor: Decimal) -> tuple[int, Decimal]:
    if factor <= 0:
        return 0, total
    cajas = int(total // factor)
    unidades = total - cajas * factor
    return cajas, unidades


def _estado_lote(fecha_venc: date | None, categoria: Categoria | None, hoy: date) -> tuple[str, int | None]:
    if fecha_venc is None:
        return "sin_fecha", None
    dias = (fecha_venc - hoy).days
    return clasificar(dias, _umbrales_de(categoria)).value, dias


def listar_vista(
    db: Session,
    *,
    q: str | None = None,
    estado: str | None = None,
    sucursal_id: int | None = None,
    sin_fecha: bool = False,
    hoy: date | None = None,
) -> list[dict]:
    hoy = hoy or date.today()

    # Existencias por lote (opcionalmente filtradas por sucursal).
    exist_stmt = (
        select(
            InventarioLote.lote_id,
            func.sum(InventarioLote.cantidad).label("total"),
            func.count(func.distinct(InventarioLote.bodega_id)).label("n_bodegas"),
        )
        .join(Bodega, Bodega.id == InventarioLote.bodega_id)
        .group_by(InventarioLote.lote_id)
    )
    if sucursal_id is not None:
        exist_stmt = exist_stmt.where(Bodega.sucursal_id == sucursal_id)
    existencias = {
        r.lote_id: (r.total or Decimal(0), r.n_bodegas) for r in db.execute(exist_stmt).all()
    }

    # Ultima inspeccion por lote.
    insp_rows = db.execute(
        select(Inspeccion.lote_id, func.max(Inspeccion.fecha_inspeccion))
        .group_by(Inspeccion.lote_id)
    ).all()
    ultima_insp = {lote_id: fecha for lote_id, fecha in insp_rows}

    # Lotes activos + producto + categoria.
    lotes_stmt = (
        select(Lote, Producto, Categoria)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Categoria, Categoria.id == Producto.categoria_id, isouter=True)
        .where(Lote.activo.is_(True))
    )
    if q:
        like = f"%{q}%"
        lotes_stmt = lotes_stmt.where(
            Producto.sku.ilike(like)
            | Producto.descripcion.ilike(like)
            | Lote.numero_lote.ilike(like)
        )

    filas: list[dict] = []
    for lote, producto, categoria in db.execute(lotes_stmt).all():
        total, n_bodegas = existencias.get(lote.id, (Decimal(0), 0))
        # Si se filtra por sucursal y el lote no tiene existencia ahi, omitir.
        if sucursal_id is not None and lote.id not in existencias:
            continue
        est, dias = _estado_lote(lote.fecha_vencimiento, categoria, hoy)
        if sin_fecha and est != "sin_fecha":
            continue
        if estado and est != estado:
            continue
        cajas, unidades = _cajas_unidades(total, producto.factor_empaque)
        filas.append(
            {
                "id": lote.id,
                "producto_id": producto.id,
                "producto_sku": producto.sku,
                "producto_descripcion": producto.descripcion,
                "numero_lote": lote.numero_lote,
                "fecha_vencimiento": lote.fecha_vencimiento,
                "dias_restantes": dias,
                "existencia_total": total,
                "cajas": cajas,
                "unidades": unidades,
                "n_bodegas": n_bodegas,
                "estado": est,
                "ultima_inspeccion": ultima_insp.get(lote.id),
            }
        )

    # Orden: sin_fecha y menos dias primero (mas urgente arriba).
    def _clave(f: dict):
        d = f["dias_restantes"]
        return (d is None, d if d is not None else 0)

    filas.sort(key=_clave)
    return filas


def detalle(db: Session, lote_id: int, *, hoy: date | None = None) -> dict | None:
    hoy = hoy or date.today()
    row = db.execute(
        select(Lote, Producto, Categoria, Proveedor)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Categoria, Categoria.id == Producto.categoria_id, isouter=True)
        .join(Proveedor, Proveedor.id == Producto.proveedor_id, isouter=True)
        .where(Lote.id == lote_id)
    ).first()
    if row is None:
        return None
    lote, producto, categoria, proveedor = row

    existencias = [
        {
            "bodega_id": bid,
            "bodega_nombre": bnom,
            "sucursal_nombre": snom,
            "cantidad": cant,
        }
        for bid, bnom, snom, cant in db.execute(
            select(Bodega.id, Bodega.nombre, Sucursal.nombre, InventarioLote.cantidad)
            .join(Bodega, Bodega.id == InventarioLote.bodega_id)
            .join(Sucursal, Sucursal.id == Bodega.sucursal_id)
            .where(InventarioLote.lote_id == lote_id)
        ).all()
    ]
    total = sum((e["cantidad"] for e in existencias), Decimal(0))

    inspecciones = [
        {
            "id": iid,
            "fecha_inspeccion": fecha,
            "responsable": resp,
            "cantidad_contada": cant,
            "observaciones": obs,
        }
        for iid, fecha, resp, cant, obs in db.execute(
            select(
                Inspeccion.id,
                Inspeccion.fecha_inspeccion,
                Usuario.nombre,
                Inspeccion.cantidad_contada,
                Inspeccion.observaciones,
            )
            .join(Usuario, Usuario.id == Inspeccion.responsable_id)
            .where(Inspeccion.lote_id == lote_id)
            .order_by(Inspeccion.fecha_inspeccion.desc())
            .limit(10)
        ).all()
    ]

    est, dias = _estado_lote(lote.fecha_vencimiento, categoria, hoy)

    return {
        "id": lote.id,
        "producto_sku": producto.sku,
        "producto_descripcion": producto.descripcion,
        "categoria": categoria.nombre if categoria else None,
        "proveedor": proveedor.nombre if proveedor else None,
        "unidad_base": producto.unidad_base,
        "factor_empaque": producto.factor_empaque,
        "numero_lote": lote.numero_lote,
        "fecha_vencimiento": lote.fecha_vencimiento,
        "fecha_fabricacion": lote.fecha_fabricacion,
        "dias_restantes": dias,
        "estado": est,
        "existencia_total": total,
        "existencias": existencias,
        "inspecciones": inspecciones,
    }
