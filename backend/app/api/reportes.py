from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services import reportes as svc

router = APIRouter(prefix="/reportes", tags=["reportes"])

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/tipos")
def tipos() -> list[dict]:
    return [{"tipo": t, "titulo": titulo} for t, titulo in svc.TITULOS.items()]


def _filtros(
    q: str | None, estado: str | None, sucursal_id: int | None, disposicion: str | None
) -> dict:
    return {"q": q, "estado": estado, "sucursal_id": sucursal_id, "disposicion": disposicion}


@router.get("/{tipo}/preview")
def preview(
    tipo: str,
    q: str | None = None,
    estado: str | None = None,
    sucursal_id: int | None = None,
    disposicion: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        return svc.construir(db, tipo, _filtros(q, estado, sucursal_id, disposicion))
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("/{tipo}/excel")
def excel(
    tipo: str,
    q: str | None = None,
    estado: str | None = None,
    sucursal_id: int | None = None,
    disposicion: str | None = None,
    db: Session = Depends(get_db),
):
    try:
        contenido = svc.exportar_excel(db, tipo, _filtros(q, estado, sucursal_id, disposicion))
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    fecha = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    nombre = f"reporte_{tipo}_{fecha}.xlsx"
    return Response(
        content=contenido,
        media_type=XLSX_MIME,
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )
