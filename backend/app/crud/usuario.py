from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.seguridad import Usuario
from app.schemas.auth import UsuarioCreate, UsuarioUpdate


def get(db: Session, id: int) -> Usuario | None:
    return db.get(Usuario, id)


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.scalar(select(Usuario).where(Usuario.email == email))


def listar(db: Session, *, skip: int = 0, limit: int = 100) -> list[Usuario]:
    stmt = select(Usuario).offset(skip).limit(limit).order_by(Usuario.id)
    return list(db.scalars(stmt).all())


def create(db: Session, obj_in: UsuarioCreate) -> Usuario:
    data = obj_in.model_dump(exclude={"password"})
    db_obj = Usuario(**data, password_hash=hash_password(obj_in.password))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(db: Session, db_obj: Usuario, obj_in: UsuarioUpdate) -> Usuario:
    data = obj_in.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for key, value in data.items():
        setattr(db_obj, key, value)
    if password:
        db_obj.password_hash = hash_password(password)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, id: int) -> Usuario | None:
    obj = db.get(Usuario, id)
    if obj is not None:
        db.delete(obj)
        db.commit()
    return obj
