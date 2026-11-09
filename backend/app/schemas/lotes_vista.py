from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class LoteVistaRow(BaseModel):
    """Fila de la tabla de lotes y vencimientos (datos calculados)."""

    id: int
    producto_id: int
    producto_sku: str
    producto_descripcion: str
    numero_lote: str
    fecha_vencimiento: date | None
    dias_restantes: int | None
    existencia_total: Decimal
    cajas: int
    unidades: Decimal
    n_bodegas: int
    estado: str  # estado_alerta o 'sin_fecha'
    ultima_inspeccion: datetime | None


class ExistenciaBodega(BaseModel):
    bodega_id: int
    bodega_nombre: str
    sucursal_nombre: str
    cantidad: Decimal
    # Desglose declarado por el encargado; None si no se declaro.
    cajas: Decimal | None = None
    unidades_sueltas: Decimal | None = None


class InspeccionResumen(BaseModel):
    id: int
    fecha_inspeccion: datetime
    responsable: str
    cantidad_contada: Decimal | None
    observaciones: str | None


class LoteDetalle(BaseModel):
    id: int
    producto_sku: str
    producto_descripcion: str
    categoria: str | None
    proveedor: str | None
    unidad_base: str
    factor_empaque: Decimal
    numero_lote: str
    fecha_vencimiento: date | None
    fecha_fabricacion: date | None
    dias_restantes: int | None
    estado: str
    existencia_total: Decimal
    existencias: list[ExistenciaBodega]
    inspecciones: list[InspeccionResumen]
