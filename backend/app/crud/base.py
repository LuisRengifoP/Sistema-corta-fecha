from __future__ import annotations

from typing import Generic, Sequence, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)
CreateT = TypeVar("CreateT", bound=BaseModel)
UpdateT = TypeVar("UpdateT", bound=BaseModel)


class CRUDBase(Generic[ModelT, CreateT, UpdateT]):
    """CRUD generico sincrono sobre un modelo SQLAlchemy."""

    def __init__(self, model: type[ModelT]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelT | None:
        return db.get(self.model, id)

    def list(self, db: Session, *, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
        stmt = select(self.model).offset(skip).limit(limit).order_by(self.model.id)
        return db.scalars(stmt).all()

    def count(self, db: Session) -> int:
        return db.scalar(select(func.count()).select_from(self.model)) or 0

    def create(self, db: Session, obj_in: CreateT) -> ModelT:
        db_obj = self.model(**obj_in.model_dump(exclude_unset=True))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelT, obj_in: UpdateT) -> ModelT:
        for key, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, key, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> ModelT | None:
        obj = db.get(self.model, id)
        if obj is not None:
            db.delete(obj)
            db.commit()
        return obj
