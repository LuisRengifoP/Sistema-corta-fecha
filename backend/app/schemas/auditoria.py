from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import AccionAuditoria


class HistorialRead(BaseModel):
    id: int
    tabla: str
    registro_id: int
    accion: AccionAuditoria
    usuario_id: int | None = None
    usuario_nombre: str | None = None
    datos_antes: dict | None = None
    datos_despues: dict | None = None
    created_at: datetime


class HistorialPage(BaseModel):
    """Pagina de resultados para tablas extensas (paginacion en servidor)."""

    items: list[HistorialRead]
    total: int
    skip: int
    limit: int
