"""Modelos ORM SQLAlchemy 2.x.

Importa todos los modelos para que queden registrados en Base.metadata
(Alembic autogenerate y creacion de tablas los descubren desde aqui).
"""

from app.core.database import Base
from app.models.auditoria import AlertaEjecucion, HistorialCambio
from app.models.catalogo import Categoria, Producto, Proveedor
from app.models.inventario import (
    InventarioLote,
    InventarioMovimiento,
    Lote,
)
from app.models.operacion import (
    AccionGestion,
    Alerta,
    Inspeccion,
    InspeccionEvidencia,
    Novedad,
    NovedadEvidencia,
)
from app.models.seguridad import (
    Bodega,
    Permiso,
    Rol,
    RolPermiso,
    Sucursal,
    Usuario,
)

__all__ = [
    "Base",
    "Rol",
    "Permiso",
    "RolPermiso",
    "Sucursal",
    "Bodega",
    "Usuario",
    "Categoria",
    "Proveedor",
    "Producto",
    "Lote",
    "InventarioLote",
    "InventarioMovimiento",
    "Inspeccion",
    "InspeccionEvidencia",
    "Novedad",
    "NovedadEvidencia",
    "Alerta",
    "AccionGestion",
    "HistorialCambio",
    "AlertaEjecucion",
]
