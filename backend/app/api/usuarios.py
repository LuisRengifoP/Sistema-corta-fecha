from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import usuario as crud
from app.schemas.auth import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("", response_model=list[UsuarioRead])
def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.listar(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=UsuarioRead)
def obtener(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    return obj


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear(payload: UsuarioCreate, db: Session = Depends(get_db)):
    if crud.get_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email ya registrado")
    try:
        return crud.create(db, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Viola una restriccion") from exc


@router.patch("/{item_id}", response_model=UsuarioRead)
def actualizar(item_id: int, payload: UsuarioUpdate, db: Session = Depends(get_db)):
    obj = crud.get(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
    try:
        return crud.update(db, obj, payload)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Viola una restriccion") from exc


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(item_id: int, db: Session = Depends(get_db)):
    obj = crud.remove(db, item_id)
    if obj is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
