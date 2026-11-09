from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.crud import usuario as crud_usuario
from app.models.seguridad import Usuario
from app.schemas.auth import Token, UsuarioRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    # OAuth2PasswordRequestForm usa 'username'; aqui lo tratamos como email.
    user = crud_usuario.get_by_email(db, form.username)
    if user is None or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Email o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.activo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuario inactivo")

    user.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(user.id, extra={"rol_id": user.rol_id})
    return Token(access_token=token)


@router.get("/me", response_model=UsuarioRead)
def me(user: Usuario = Depends(get_current_user)) -> Usuario:
    return user
