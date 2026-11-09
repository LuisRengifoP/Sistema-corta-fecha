from typing import Type

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud.base import CRUDBase


def make_crud_router(
    *,
    prefix: str,
    tags: list[str],
    crud: CRUDBase,
    read_schema: Type[BaseModel],
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
) -> APIRouter:
    """Construye un router REST estandar (list/get/create/update/delete)."""

    router = APIRouter(prefix=prefix, tags=tags)

    @router.get("", response_model=list[read_schema])
    def listar(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        return crud.list(db, skip=skip, limit=limit)

    @router.get("/{item_id}", response_model=read_schema)
    def obtener(item_id: int, db: Session = Depends(get_db)):
        obj = crud.get(db, item_id)
        if obj is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "No encontrado")
        return obj

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def crear(payload: create_schema, db: Session = Depends(get_db)):
        try:
            return crud.create(db, payload)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "Viola una restriccion") from exc

    @router.patch("/{item_id}", response_model=read_schema)
    def actualizar(item_id: int, payload: update_schema, db: Session = Depends(get_db)):
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

    return router
