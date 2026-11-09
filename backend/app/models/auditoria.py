from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._common import CreatedAtMixin, pg_enum
from app.models.enums import AccionAuditoria
from app.models.seguridad import Usuario


class HistorialCambio(CreatedAtMixin, Base):
    __tablename__ = "historial_cambios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tabla: Mapped[str] = mapped_column(Text, nullable=False)
    registro_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    accion: Mapped[AccionAuditoria] = mapped_column(
        pg_enum(AccionAuditoria, "accion_auditoria"), nullable=False
    )
    usuario_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("usuarios.id", ondelete="SET NULL")
    )
    datos_antes: Mapped[dict | None] = mapped_column(JSONB)
    datos_despues: Mapped[dict | None] = mapped_column(JSONB)

    usuario: Mapped[Usuario | None] = relationship()


class AlertaEjecucion(Base):
    __tablename__ = "alerta_ejecuciones"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    iniciada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finalizada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lotes_evaluados: Mapped[int | None] = mapped_column(Integer)
    alertas_creadas: Mapped[int | None] = mapped_column(Integer)
    alertas_actualizadas: Mapped[int | None] = mapped_column(Integer)
    lotes_sin_fecha: Mapped[int | None] = mapped_column(Integer)
    resultado: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[str | None] = mapped_column(Text)
