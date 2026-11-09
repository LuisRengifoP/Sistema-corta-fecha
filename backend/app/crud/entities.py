"""Instancias CRUD por entidad.

La mayoria usa CRUDBase directamente. Casos con reglas propias extienden la clase.
"""

from app.crud.base import CRUDBase
from app.models.catalogo import Categoria, Producto, Proveedor
from app.models.inventario import InventarioLote, Lote
from app.models.operacion import Alerta, Inspeccion, Novedad
from app.models.seguridad import Bodega, Rol, Sucursal
from app.schemas.auth import RolCreate, RolUpdate
from app.schemas.catalogo import (
    CategoriaCreate,
    CategoriaUpdate,
    ProductoCreate,
    ProductoUpdate,
    ProveedorCreate,
    ProveedorUpdate,
)
from app.schemas.inventario import (
    InventarioLoteCreate,
    InventarioLoteUpdate,
    LoteCreate,
    LoteUpdate,
)
from app.schemas.operacion import (
    AlertaSeguimientoUpdate,
    InspeccionCreate,
    InspeccionUpdate,
    NovedadCreate,
    NovedadUpdate,
)
from app.schemas.seguridad import (
    BodegaCreate,
    BodegaUpdate,
    SucursalCreate,
    SucursalUpdate,
)

rol = CRUDBase[Rol, RolCreate, RolUpdate](Rol)
sucursal = CRUDBase[Sucursal, SucursalCreate, SucursalUpdate](Sucursal)
bodega = CRUDBase[Bodega, BodegaCreate, BodegaUpdate](Bodega)
categoria = CRUDBase[Categoria, CategoriaCreate, CategoriaUpdate](Categoria)
proveedor = CRUDBase[Proveedor, ProveedorCreate, ProveedorUpdate](Proveedor)
producto = CRUDBase[Producto, ProductoCreate, ProductoUpdate](Producto)
lote = CRUDBase[Lote, LoteCreate, LoteUpdate](Lote)
inventario_lote = CRUDBase[InventarioLote, InventarioLoteCreate, InventarioLoteUpdate](
    InventarioLote
)
inspeccion = CRUDBase[Inspeccion, InspeccionCreate, InspeccionUpdate](Inspeccion)
novedad = CRUDBase[Novedad, NovedadCreate, NovedadUpdate](Novedad)
# Alerta: solo lectura + actualizar seguimiento (no create/delete por API).
alerta = CRUDBase[Alerta, AlertaSeguimientoUpdate, AlertaSeguimientoUpdate](Alerta)
