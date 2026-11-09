from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.auditoria import HistorialCambio
from app.models.enums import AccionAuditoria
from app.models.seguridad import Usuario
from app.schemas.auditoria import HistorialPage, HistorialRead

router = APIRouter(prefix="/historial", tags=["historial"])


@router.get("", response_model=HistorialPage)
def listar(
    tabla: str | None = None,
    accion: AccionAuditoria | None = None,
    usuario_id: int | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> HistorialPage:
    """Lista el historial de cambios con filtros y paginacion en servidor."""

    filtros = []
    if tabla:
        filtros.append(HistorialCambio.tabla == tabla)
    if accion is not None:
        filtros.append(HistorialCambio.accion == accion)
    if usuario_id is not None:
        filtros.append(HistorialCambio.usuario_id == usuario_id)
    if desde is not None:
        filtros.append(HistorialCambio.created_at >= desde)
    if hasta is not None:
        filtros.append(HistorialCambio.created_at <= hasta)

    total = (
        db.scalar(
            select(func.count()).select_from(HistorialCambio).where(*filtros)
        )
        or 0
    )

    stmt = (
        select(HistorialCambio, Usuario.nombre)
        .outerjoin(Usuario, HistorialCambio.usuario_id == Usuario.id)
        .where(*filtros)
        .order_by(HistorialCambio.created_at.desc(), HistorialCambio.id.desc())
        .offset(skip)
        .limit(limit)
    )

    items = [
        HistorialRead(
            id=h.id,
            tabla=h.tabla,
            registro_id=h.registro_id,
            accion=h.accion,
            usuario_id=h.usuario_id,
            usuario_nombre=nombre,
            datos_antes=h.datos_antes,
            datos_despues=h.datos_despues,
            created_at=h.created_at,
        )
        for h, nombre in db.execute(stmt).all()
    ]

    return HistorialPage(items=items, total=total, skip=skip, limit=limit)


@router.get("/tablas", response_model=list[str])
def tablas(db: Session = Depends(get_db)) -> list[str]:
    """Tablas distintas presentes en el historial (para el filtro)."""
    stmt = select(HistorialCambio.tabla).distinct().order_by(HistorialCambio.tabla)
    return list(db.scalars(stmt).all())
