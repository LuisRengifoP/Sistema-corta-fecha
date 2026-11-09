from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import entities as crud
from app.models.auditoria import AlertaEjecucion
from app.models.enums import EstadoAccion, EstadoSeguimiento
from app.models.operacion import AccionGestion
from app.schemas.operacion import (
    AlertaRead,
    AlertaSeguimientoUpdate,
    AlertaVistaRow,
    GestionRequest,
)
from app.services.alertas import calcular_alertas
from app.services.alertas_vista import listar_vista

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get("/vista", response_model=list[AlertaVistaRow])
def vista(
    estado: str | None = None,
    seguimiento: str | None = None,
    sin_responsable: bool = False,
    db: Session = Depends(get_db),
):
    return listar_vista(
        db, estado=estado, seguimiento=seguimiento, sin_responsable=sin_responsable
    )


@router.post("/{item_id}/gestion", response_model=AlertaRead)
def gestionar(item_id: int, payload: GestionRequest, db: Session = Depends(get_db)):
    alerta = crud.alerta.get(db, item_id)
    if alerta is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alerta no encontrada")
    if payload.cerrar and not (payload.resultado and payload.resultado.strip()):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "El resultado es obligatorio al cerrar la gestion"
        )

    accion = AccionGestion(
        alerta_id=alerta.id,
        responsable_id=payload.responsable_id,
        descripcion=payload.descripcion,
        estado=EstadoAccion.cerrada if payload.cerrar else EstadoAccion.abierta,
        resultado=payload.resultado,
        cerrada_en=datetime.now(timezone.utc) if payload.cerrar else None,
    )
    db.add(accion)
    alerta.seguimiento = (
        EstadoSeguimiento.gestionada if payload.cerrar else EstadoSeguimiento.en_gestion
    )
    db.commit()
    db.refresh(alerta)
    return alerta


@router.post("/recalcular", status_code=status.HTTP_200_OK)
def recalcular(db: Session = Depends(get_db)) -> dict:
    """Ejecuta el calculo de alertas y registra la corrida en alerta_ejecuciones."""
    ejec = AlertaEjecucion()
    db.add(ejec)
    db.commit()
    db.refresh(ejec)
    try:
        r = calcular_alertas(db)
    except Exception as exc:  # noqa: BLE001
        ejec.finalizada_en = datetime.now(timezone.utc)
        ejec.resultado = "error"
        ejec.detalle = str(exc)
        db.commit()
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Fallo el calculo") from exc

    ejec.finalizada_en = datetime.now(timezone.utc)
    ejec.lotes_evaluados = r.lotes_evaluados
    ejec.alertas_creadas = r.alertas_creadas
    ejec.alertas_actualizadas = r.alertas_actualizadas
    ejec.lotes_sin_fecha = r.lotes_sin_fecha
    ejec.resultado = "ok"
    db.commit()
    return {
        "ejecucion_id": ejec.id,
        "lotes_evaluados": r.lotes_evaluados,
        "alertas_creadas": r.alertas_creadas,
        "alertas_actualizadas": r.alertas_actualizadas,
        "lotes_sin_fecha": r.lotes_sin_fecha,
    }


@router.get("", response_model=list[AlertaRead])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.alerta.list(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=AlertaRead)
def obtener(item_id: int, db: Session = Depends(get_db)):
    obj = crud.alerta.get(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    return obj


@router.patch("/{item_id}", response_model=AlertaRead)
def actualizar_seguimiento(
    item_id: int, payload: AlertaSeguimientoUpdate, db: Session = Depends(get_db)
):
    obj = crud.alerta.get(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    return crud.alerta.update(db, obj, payload)
