from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.enums import (
    DisposicionNovedad,
    EstadoSeguimiento,
    TipoNovedad,
)
from app.schemas.common import ORMModel


# ---------- Inspeccion ----------
class InspeccionBase(BaseModel):
    lote_id: int
    bodega_id: int
    responsable_id: int
    cantidad_contada: Decimal | None = Field(default=None, ge=0)
    fecha_vencimiento_verificada: date | None = None
    observaciones: str | None = None


class InspeccionCreate(InspeccionBase):
    pass


class InspeccionUpdate(BaseModel):
    cantidad_contada: Decimal | None = Field(default=None, ge=0)
    fecha_vencimiento_verificada: date | None = None
    observaciones: str | None = None


class InspeccionRead(InspeccionBase, ORMModel):
    id: int
    fecha_inspeccion: datetime


# ---------- Novedad ----------
class NovedadBase(BaseModel):
    lote_id: int
    bodega_id: int
    inspeccion_id: int | None = None
    tipo: TipoNovedad
    cantidad_afectada: Decimal = Field(gt=0)
    disposicion: DisposicionNovedad = DisposicionNovedad.pendiente
    reportado_por_id: int
    observaciones: str | None = None


class NovedadCreate(NovedadBase):
    pass


class NovedadUpdate(BaseModel):
    tipo: TipoNovedad | None = None
    cantidad_afectada: Decimal | None = Field(default=None, gt=0)
    disposicion: DisposicionNovedad | None = None
    observaciones: str | None = None


class NovedadRead(NovedadBase, ORMModel):
    id: int


# ---------- Alerta (solo lectura + cambio de seguimiento) ----------
class AlertaRead(ORMModel):
    id: int
    lote_id: int
    sucursal_id: int
    estado: str
    seguimiento: EstadoSeguimiento
    dias_restantes: int | None
    cantidad_en_riesgo: Decimal | None
    periodo: str
    calculada_en: datetime
    actualizada_en: datetime


class AlertaSeguimientoUpdate(BaseModel):
    seguimiento: EstadoSeguimiento


class AlertaVistaRow(ORMModel):
    id: int
    lote_id: int
    producto_sku: str
    producto_descripcion: str
    numero_lote: str
    sucursal_nombre: str
    estado: str
    seguimiento: EstadoSeguimiento
    dias_restantes: int | None
    cantidad_en_riesgo: Decimal | None
    calculada_en: datetime
    responsable: str | None
    tiene_inspeccion: bool


class GestionRequest(BaseModel):
    responsable_id: int
    descripcion: str
    cerrar: bool = False
    resultado: str | None = None
