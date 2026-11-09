from __future__ import annotations

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.models.catalogo import Producto
from app.models.inventario import Lote
from app.models.operacion import AccionGestion, Alerta, Inspeccion
from app.models.seguridad import Sucursal, Usuario


def listar_vista(
    db: Session,
    *,
    estado: str | None = None,
    seguimiento: str | None = None,
    sin_responsable: bool = False,
) -> list[dict]:
    # Responsable = responsable de la ultima accion de gestion de la alerta.
    ultima_accion = (
        select(
            AccionGestion.alerta_id,
            func.max(AccionGestion.id).label("max_id"),
        )
        .where(AccionGestion.alerta_id.is_not(None))
        .group_by(AccionGestion.alerta_id)
        .subquery()
    )

    stmt = (
        select(
            Alerta,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Sucursal.nombre,
            Usuario.nombre,
            exists().where(Inspeccion.lote_id == Alerta.lote_id).label("tiene_insp"),
        )
        .join(Lote, Lote.id == Alerta.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Sucursal, Sucursal.id == Alerta.sucursal_id)
        .join(ultima_accion, ultima_accion.c.alerta_id == Alerta.id, isouter=True)
        .join(AccionGestion, AccionGestion.id == ultima_accion.c.max_id, isouter=True)
        .join(Usuario, Usuario.id == AccionGestion.responsable_id, isouter=True)
    )
    if estado:
        stmt = stmt.where(Alerta.estado == estado)
    if seguimiento:
        stmt = stmt.where(Alerta.seguimiento == seguimiento)
    if sin_responsable:
        stmt = stmt.where(Usuario.nombre.is_(None))

    stmt = stmt.order_by(Alerta.dias_restantes.asc().nulls_first())

    filas: list[dict] = []
    for alerta, sku, desc, numlote, suc, resp, tiene_insp in db.execute(stmt).all():
        filas.append(
            {
                "id": alerta.id,
                "lote_id": alerta.lote_id,
                "producto_sku": sku,
                "producto_descripcion": desc,
                "numero_lote": numlote,
                "sucursal_nombre": suc,
                "estado": alerta.estado.value,
                "seguimiento": alerta.seguimiento.value,
                "dias_restantes": alerta.dias_restantes,
                "cantidad_en_riesgo": alerta.cantidad_en_riesgo,
                "calculada_en": alerta.calculada_en,
                "responsable": resp,
                "tiene_inspeccion": bool(tiene_insp),
            }
        )
    return filas
