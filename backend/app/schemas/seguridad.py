from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import ORMModel


# ---------- Sucursal ----------
class SucursalBase(BaseModel):
    codigo: str
    nombre: str
    direccion: str | None = None
    activa: bool = True


class SucursalCreate(SucursalBase):
    pass


class SucursalUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    direccion: str | None = None
    activa: bool | None = None


class SucursalRead(SucursalBase, ORMModel):
    id: int


# ---------- Bodega ----------
class BodegaBase(BaseModel):
    sucursal_id: int
    codigo: str
    nombre: str
    activa: bool = True


class BodegaCreate(BodegaBase):
    pass


class BodegaUpdate(BaseModel):
    sucursal_id: int | None = None
    codigo: str | None = None
    nombre: str | None = None
    activa: bool | None = None


class BodegaRead(BodegaBase, ORMModel):
    id: int
