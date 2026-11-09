"""Crea un rol 'admin' y un usuario administrador inicial.

Uso:
    cd backend
    python -m scripts.seed_admin

Variables de entorno:
    ADMIN_EMAIL     (default admin@corta-fecha.local)
    ADMIN_PASSWORD  (default admin1234)  <-- cambiar tras el primer login
    ADMIN_NOMBRE    (default Administrador)
"""

import os

from app.core.database import SessionLocal
from app.crud import usuario as crud_usuario
from app.models.seguridad import Rol
from app.schemas.auth import UsuarioCreate


def main() -> None:
    email = os.getenv("ADMIN_EMAIL", "admin@corta-fecha.com")
    password = os.getenv("ADMIN_PASSWORD", "admin1234")
    nombre = os.getenv("ADMIN_NOMBRE", "Administrador")

    db = SessionLocal()
    try:
        rol = db.query(Rol).filter(Rol.nombre == "admin").one_or_none()
        if rol is None:
            rol = Rol(nombre="admin", descripcion="Acceso total")
            db.add(rol)
            db.commit()
            db.refresh(rol)
            print(f"Rol 'admin' creado (id={rol.id})")

        if crud_usuario.get_by_email(db, email):
            print(f"Usuario {email} ya existe. Nada que hacer.")
            return

        crud_usuario.create(
            db,
            UsuarioCreate(
                email=email, nombre=nombre, rol_id=rol.id, password=password
            ),
        )
        print(f"Usuario admin creado: {email}")
        print("IMPORTANTE: cambia la contrasena tras el primer login.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
