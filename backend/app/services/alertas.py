from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.catalogo import Categoria, Producto
from app.models.enums import EstadoAlerta
from app.models.inventario import InventarioLote, Lote
from app.models.operacion import Alerta
from app.models.seguridad import Bodega

# Umbrales por defecto (dias restantes). Ajustables por categoria.
DEFAULT_PREVENTIVA = 90
DEFAULT_PRIORITARIA = 60
DEFAULT_CRITICA = 30


@dataclass
class Umbrales:
    preventiva: int
    prioritaria: int
    critica: int


def _umbrales_de(categoria: Categoria | None) -> Umbrales:
    if categoria is None:
        return Umbrales(DEFAULT_PREVENTIVA, DEFAULT_PRIORITARIA, DEFAULT_CRITICA)
    return Umbrales(
        preventiva=categoria.dias_preventiva or DEFAULT_PREVENTIVA,
        prioritaria=categoria.dias_prioritaria or DEFAULT_PRIORITARIA,
        critica=categoria.dias_critica or DEFAULT_CRITICA,
    )


def clasificar(dias_restantes: int, u: Umbrales) -> EstadoAlerta:
    if dias_restantes < 0:
        return EstadoAlerta.vencido
    if dias_restantes <= u.critica:
        return EstadoAlerta.critica
    if dias_restantes <= u.prioritaria:
        return EstadoAlerta.prioritaria
    if dias_restantes <= u.preventiva:
        return EstadoAlerta.preventiva
    return EstadoAlerta.normal


@dataclass
class ResultadoCalculo:
    lotes_evaluados: int
    alertas_creadas: int
    alertas_actualizadas: int
    lotes_sin_fecha: int


def _periodo_actual() -> str:
    return date.today().strftime("%Y-%m")


def calcular_alertas(
    db: Session, *, hoy: date | None = None, periodo: str | None = None
) -> ResultadoCalculo:
    """Clasifica lotes activos por vencimiento y hace upsert de alertas.

    - Existencia en riesgo = suma por lote + sucursal (join bodega->sucursal).
    - Solo genera alerta para estados distintos de 'normal'.
    - No duplica: una fila por (lote, sucursal, periodo).
    - Una alerta es un calculo; no equivale a inspeccion fisica.
    """
    hoy = hoy or date.today()
    periodo = periodo or _periodo_actual()

    creadas = 0
    actualizadas = 0
    lotes_sin_fecha = 0

    # Existencias por lote + sucursal (solo cantidad > 0).
    existencias = db.execute(
        select(
            InventarioLote.lote_id,
            Bodega.sucursal_id,
            func.sum(InventarioLote.cantidad).label("cantidad"),
        )
        .join(Bodega, Bodega.id == InventarioLote.bodega_id)
        .where(InventarioLote.cantidad > 0)
        .group_by(InventarioLote.lote_id, Bodega.sucursal_id)
    ).all()

    # Lotes activos con su categoria (para umbrales).
    lotes = db.execute(
        select(Lote, Categoria)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Categoria, Categoria.id == Producto.categoria_id, isouter=True)
        .where(Lote.activo.is_(True))
    ).all()
    lote_map: dict[int, tuple[Lote, Categoria | None]] = {
        lote.id: (lote, cat) for lote, cat in lotes
    }

    lotes_evaluados = len(lote_map)

    # Lotes activos sin fecha de vencimiento = dato inconsistente a revisar.
    for lote, _cat in lote_map.values():
        if lote.fecha_vencimiento is None:
            lotes_sin_fecha += 1

    for lote_id, sucursal_id, cantidad in existencias:
        entry = lote_map.get(lote_id)
        if entry is None:
            continue
        lote, categoria = entry
        if lote.fecha_vencimiento is None:
            continue  # sin fecha: no se clasifica, ya contado arriba

        dias = (lote.fecha_vencimiento - hoy).days
        estado = clasificar(dias, _umbrales_de(categoria))
        if estado == EstadoAlerta.normal:
            continue

        alerta = db.scalar(
            select(Alerta).where(
                Alerta.lote_id == lote_id,
                Alerta.sucursal_id == sucursal_id,
                Alerta.periodo == periodo,
            )
        )
        if alerta is None:
            db.add(
                Alerta(
                    lote_id=lote_id,
                    sucursal_id=sucursal_id,
                    estado=estado,
                    dias_restantes=dias,
                    cantidad_en_riesgo=Decimal(cantidad),
                    periodo=periodo,
                )
            )
            creadas += 1
        else:
            alerta.estado = estado
            alerta.dias_restantes = dias
            alerta.cantidad_en_riesgo = Decimal(cantidad)
            alerta.actualizada_en = datetime.now(timezone.utc)
            actualizadas += 1

    db.commit()
    return ResultadoCalculo(lotes_evaluados, creadas, actualizadas, lotes_sin_fecha)
