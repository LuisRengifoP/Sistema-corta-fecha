from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._common import CreatedAtMixin, TimestampMixin
from app.models.catalogo import Producto
from app.models.enums import TipoMovimiento
from app.models.seguridad import Bodega, Usuario
from app.models._common import pg_enum


class Lote(TimestampMixin, Base):
    __tablename__ = "lotes"
    __table_args__ = (UniqueConstraint("producto_id", "numero_lote"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    producto_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("productos.id", ondelete="RESTRICT"), nullable=False
    )
    numero_lote: Mapped[str] = mapped_column(Text, nullable=False)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date)
    fecha_fabricacion: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    producto: Mapped[Producto] = relationship(back_populates="lotes")
    existencias: Mapped[list[InventarioLote]] = relationship(back_populates="lote")


class InventarioLote(Base):
    __tablename__ = "inventario_lotes"
    __table_args__ = (UniqueConstraint("lote_id", "bodega_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False
    )
    bodega_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bodegas.id", ondelete="RESTRICT"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    lote: Mapped[Lote] = relationship(back_populates="existencias")
    bodega: Mapped[Bodega] = relationship()


class InventarioMovimiento(CreatedAtMixin, Base):
    __tablename__ = "inventario_movimientos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False
    )
    bodega_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bodegas.id", ondelete="RESTRICT"), nullable=False
    )
    tipo: Mapped[TipoMovimiento] = mapped_column(
        pg_enum(TipoMovimiento, "tipo_movimiento"), nullable=False
    )
    cantidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    bodega_destino_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("bodegas.id", ondelete="RESTRICT")
    )
    referencia: Mapped[str | None] = mapped_column(Text)
    usuario_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    observacion: Mapped[str | None] = mapped_column(Text)

    lote: Mapped[Lote] = relationship()
    bodega: Mapped[Bodega] = relationship(foreign_keys=[bodega_id])
    bodega_destino: Mapped[Bodega | None] = relationship(foreign_keys=[bodega_destino_id])
    usuario: Mapped[Usuario | None] = relationship()
