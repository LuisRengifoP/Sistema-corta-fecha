from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
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
from app.models._common import CreatedAtMixin, TimestampMixin, pg_enum
from app.models.enums import (
    DisposicionNovedad,
    EstadoAccion,
    EstadoAlerta,
    EstadoSeguimiento,
    TipoNovedad,
)
from app.models.inventario import Lote
from app.models.seguridad import Bodega, Sucursal, Usuario


class Inspeccion(CreatedAtMixin, Base):
    __tablename__ = "inspecciones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False
    )
    bodega_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bodegas.id", ondelete="RESTRICT"), nullable=False
    )
    responsable_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    fecha_inspeccion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cantidad_contada: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    fecha_vencimiento_verificada: Mapped[date | None] = mapped_column(Date)
    observaciones: Mapped[str | None] = mapped_column(Text)

    lote: Mapped[Lote] = relationship()
    bodega: Mapped[Bodega] = relationship()
    responsable: Mapped[Usuario] = relationship()
    evidencias: Mapped[list[InspeccionEvidencia]] = relationship(
        back_populates="inspeccion", cascade="all, delete-orphan"
    )


class InspeccionEvidencia(CreatedAtMixin, Base):
    __tablename__ = "inspeccion_evidencias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    inspeccion_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("inspecciones.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_mime: Mapped[str | None] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)

    inspeccion: Mapped[Inspeccion] = relationship(back_populates="evidencias")


class Novedad(TimestampMixin, Base):
    __tablename__ = "novedades"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="RESTRICT"), nullable=False
    )
    bodega_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("bodegas.id", ondelete="RESTRICT"), nullable=False
    )
    inspeccion_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("inspecciones.id", ondelete="SET NULL")
    )
    tipo: Mapped[TipoNovedad] = mapped_column(
        pg_enum(TipoNovedad, "tipo_novedad"), nullable=False
    )
    cantidad_afectada: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    disposicion: Mapped[DisposicionNovedad] = mapped_column(
        pg_enum(DisposicionNovedad, "disposicion_novedad"),
        default=DisposicionNovedad.pendiente,
        nullable=False,
    )
    reportado_por_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    observaciones: Mapped[str | None] = mapped_column(Text)

    lote: Mapped[Lote] = relationship()
    bodega: Mapped[Bodega] = relationship()
    inspeccion: Mapped[Inspeccion | None] = relationship()
    reportado_por: Mapped[Usuario] = relationship()
    evidencias: Mapped[list[NovedadEvidencia]] = relationship(
        back_populates="novedad", cascade="all, delete-orphan"
    )


class NovedadEvidencia(CreatedAtMixin, Base):
    __tablename__ = "novedad_evidencias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    novedad_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("novedades.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    tipo_mime: Mapped[str | None] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)

    novedad: Mapped[Novedad] = relationship(back_populates="evidencias")


class Alerta(Base):
    __tablename__ = "alertas"
    __table_args__ = (UniqueConstraint("lote_id", "sucursal_id", "periodo"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    lote_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("lotes.id", ondelete="CASCADE"), nullable=False
    )
    sucursal_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("sucursales.id", ondelete="CASCADE"), nullable=False
    )
    estado: Mapped[EstadoAlerta] = mapped_column(
        pg_enum(EstadoAlerta, "estado_alerta"), nullable=False
    )
    seguimiento: Mapped[EstadoSeguimiento] = mapped_column(
        pg_enum(EstadoSeguimiento, "estado_seguimiento"),
        default=EstadoSeguimiento.pendiente,
        nullable=False,
    )
    dias_restantes: Mapped[int | None] = mapped_column(BigInteger)
    cantidad_en_riesgo: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    periodo: Mapped[str] = mapped_column(Text, nullable=False)
    calculada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actualizada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    lote: Mapped[Lote] = relationship()
    sucursal: Mapped[Sucursal] = relationship()


class AccionGestion(TimestampMixin, Base):
    __tablename__ = "acciones_gestion"
    __table_args__ = (
        CheckConstraint(
            "alerta_id IS NOT NULL OR novedad_id IS NOT NULL",
            name="ck_accion_alerta_o_novedad",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    alerta_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("alertas.id", ondelete="SET NULL")
    )
    novedad_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("novedades.id", ondelete="SET NULL")
    )
    responsable_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[EstadoAccion] = mapped_column(
        pg_enum(EstadoAccion, "estado_accion"),
        default=EstadoAccion.abierta,
        nullable=False,
    )
    resultado: Mapped[str | None] = mapped_column(Text)
    fecha_limite: Mapped[date | None] = mapped_column(Date)
    cerrada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    alerta: Mapped[Alerta | None] = relationship()
    novedad: Mapped[Novedad | None] = relationship()
    responsable: Mapped[Usuario] = relationship()
