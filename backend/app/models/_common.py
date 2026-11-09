"""Mixins y helpers compartidos por los modelos."""

import enum
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def pg_enum(py_enum: type[enum.Enum], name: str) -> SAEnum:
    """Reutiliza el tipo ENUM ya creado en schema.sql (no lo vuelve a crear).

    Guarda el .value del enum de Python (no el nombre del miembro).
    """
    return SAEnum(
        py_enum,
        name=name,
        create_type=False,
        values_callable=lambda e: [m.value for m in e],
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
