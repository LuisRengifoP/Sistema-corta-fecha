from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


# ---------- Lote ----------
class LoteBase(BaseModel):
    producto_id: int
    numero_lote: str
    fecha_vencimiento: date | None = None
    fecha_fabricacion: date | None = None
    activo: bool = True


class LoteCreate(LoteBase):
    pass


class LoteUpdate(BaseModel):
    numero_lote: str | None = None
    fecha_vencimiento: date | None = None
    fecha_fabricacion: date | None = None
    activo: bool | None = None


class LoteRead(LoteBase, ORMModel):
    id: int


# ---------- InventarioLote ----------
class InventarioLoteBase(BaseModel):
    lote_id: int
    bodega_id: int
    cantidad: Decimal = Field(default=Decimal(0), ge=0)


class InventarioLoteCreate(InventarioLoteBase):
    pass


class InventarioLoteUpdate(BaseModel):
    cantidad: Decimal = Field(ge=0)


class InventarioLoteRead(InventarioLoteBase, ORMModel):
    id: int
