from __future__ import annotations

from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._common import TimestampMixin


class Categoria(TimestampMixin, Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    # Umbrales de alerta por categoria; NULL = usar default global.
    dias_preventiva: Mapped[int | None] = mapped_column(Integer)
    dias_prioritaria: Mapped[int | None] = mapped_column(Integer)
    dias_critica: Mapped[int | None] = mapped_column(Integer)

    productos: Mapped[list[Producto]] = relationship(back_populates="categoria")


class Proveedor(TimestampMixin, Base):
    __tablename__ = "proveedores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    nit: Mapped[str | None] = mapped_column(Text, unique=True)
    contacto: Mapped[str | None] = mapped_column(Text)
    telefono: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    productos: Mapped[list[Producto]] = relationship(back_populates="proveedor")


class Producto(TimestampMixin, Base):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    sku: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    categoria_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("categorias.id", ondelete="SET NULL")
    )
    proveedor_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("proveedores.id", ondelete="SET NULL")
    )
    unidad_base: Mapped[str] = mapped_column(Text, default="unidad", nullable=False)
    factor_empaque: Mapped[Decimal] = mapped_column(
        Numeric(12, 3), default=1, nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria: Mapped[Categoria | None] = relationship(back_populates="productos")
    proveedor: Mapped[Proveedor | None] = relationship(back_populates="productos")
    lotes: Mapped[list["Lote"]] = relationship(back_populates="producto")  # noqa: F821
