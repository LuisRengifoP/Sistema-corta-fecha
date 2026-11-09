from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.seguridad import Permiso, RolPermiso, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

_CRED_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciales invalidas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _CRED_EXC
    user = db.get(Usuario, user_id)
    if user is None or not user.activo:
        raise _CRED_EXC
    return user


def require_permission(modulo: str, accion: str):
    """Dependencia que exige un permiso (modulo, accion) al usuario actual."""

    def checker(
        user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
    ) -> Usuario:
        stmt = (
            select(Permiso.id)
            .join(RolPermiso, RolPermiso.permiso_id == Permiso.id)
            .where(
                RolPermiso.rol_id == user.rol_id,
                Permiso.modulo == modulo,
                Permiso.accion == accion,
            )
            .limit(1)
        )
        if db.scalar(stmt) is None:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, f"Falta permiso {modulo}:{accion}"
            )
        return user

    return checker
