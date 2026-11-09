from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._common import TimestampMixin


class Rol(TimestampMixin, Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    permisos: Mapped[list[Permiso]] = relationship(
        secondary="roles_permisos", back_populates="roles"
    )
    usuarios: Mapped[list[Usuario]] = relationship(back_populates="rol")


class Permiso(Base):
    __tablename__ = "permisos"
    __table_args__ = (UniqueConstraint("modulo", "accion"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    modulo: Mapped[str] = mapped_column(Text, nullable=False)
    accion: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)

    roles: Mapped[list[Rol]] = relationship(
        secondary="roles_permisos", back_populates="permisos"
    )


class RolPermiso(Base):
    __tablename__ = "roles_permisos"

    rol_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    permiso_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True
    )


class Sucursal(TimestampMixin, Base):
    __tablename__ = "sucursales"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    codigo: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    direccion: Mapped[str | None] = mapped_column(Text)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    bodegas: Mapped[list[Bodega]] = relationship(back_populates="sucursal")


class Bodega(TimestampMixin, Base):
    __tablename__ = "bodegas"
    __table_args__ = (UniqueConstraint("sucursal_id", "codigo"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sucursal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sucursales.id", ondelete="RESTRICT"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sucursal: Mapped[Sucursal] = relationship(back_populates="bodegas")


class Usuario(TimestampMixin, Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    rol_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )
    sucursal_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("sucursales.id", ondelete="SET NULL")
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultimo_acceso: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    rol: Mapped[Rol] = relationship(back_populates="usuarios")
    sucursal: Mapped[Sucursal | None] = relationship()
