from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Rol ----------
class RolBase(BaseModel):
    nombre: str
    descripcion: str | None = None


class RolCreate(RolBase):
    pass


class RolUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None


class RolRead(RolBase, ORMModel):
    id: int


# ---------- Usuario ----------
class UsuarioBase(BaseModel):
    email: EmailStr
    nombre: str
    rol_id: int
    sucursal_id: int | None = None
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    rol_id: int | None = None
    sucursal_id: int | None = None
    activo: bool | None = None
    password: str | None = None


class UsuarioRead(UsuarioBase, ORMModel):
    id: int
    ultimo_acceso: datetime | None = None
