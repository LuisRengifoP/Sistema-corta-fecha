from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


# ---------- Categoria ----------
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str | None = None
    dias_preventiva: int | None = None
    dias_prioritaria: int | None = None
    dias_critica: int | None = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    dias_preventiva: int | None = None
    dias_prioritaria: int | None = None
    dias_critica: int | None = None


class CategoriaRead(CategoriaBase, ORMModel):
    id: int


# ---------- Proveedor ----------
class ProveedorBase(BaseModel):
    nombre: str
    nit: str | None = None
    contacto: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    nombre: str | None = None
    nit: str | None = None
    contacto: str | None = None
    telefono: str | None = None
    email: EmailStr | None = None
    activo: bool | None = None


class ProveedorRead(ProveedorBase, ORMModel):
    id: int


# ---------- Producto ----------
class ProductoBase(BaseModel):
    sku: str
    descripcion: str
    categoria_id: int | None = None
    proveedor_id: int | None = None
    unidad_base: str = "unidad"
    factor_empaque: Decimal = Field(default=Decimal(1), gt=0)
    activo: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    sku: str | None = None
    descripcion: str | None = None
    categoria_id: int | None = None
    proveedor_id: int | None = None
    unidad_base: str | None = None
    factor_empaque: Decimal | None = Field(default=None, gt=0)
    activo: bool | None = None


class ProductoRead(ProductoBase, ORMModel):
    id: int
