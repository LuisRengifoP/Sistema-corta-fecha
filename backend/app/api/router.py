"""Agrega todos los routers de la API bajo el prefijo /api/v1."""

from fastapi import APIRouter, Depends

from app.api import (
    alertas,
    dashboard,
    historial,
    inspecciones_vista,
    lotes_vista,
    novedades_vista,
    registros_corta_fecha,
    reportes,
    usuarios,
)
from app.api._crud_router import make_crud_router
from app.core.deps import get_current_user
from app.crud import entities as crud
from app.schemas import auth, catalogo, inventario, operacion, seguridad

# Todo /api/v1 exige usuario autenticado.
api_router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_current_user)])

api_router.include_router(
    make_crud_router(
        prefix="/sucursales",
        tags=["sucursales"],
        crud=crud.sucursal,
        read_schema=seguridad.SucursalRead,
        create_schema=seguridad.SucursalCreate,
        update_schema=seguridad.SucursalUpdate,
        en_uso_msg="hay bodegas o usuarios asociados a esta sucursal",
    )
)
api_router.include_router(
    make_crud_router(
        prefix="/bodegas",
        tags=["bodegas"],
        crud=crud.bodega,
        read_schema=seguridad.BodegaRead,
        create_schema=seguridad.BodegaCreate,
        update_schema=seguridad.BodegaUpdate,
        en_uso_msg="hay existencias o registros en esta bodega",
    )
)
api_router.include_router(
    make_crud_router(
        prefix="/categorias",
        tags=["categorias"],
        crud=crud.categoria,
        read_schema=catalogo.CategoriaRead,
        create_schema=catalogo.CategoriaCreate,
        update_schema=catalogo.CategoriaUpdate,
    )
)
api_router.include_router(
    make_crud_router(
        prefix="/proveedores",
        tags=["proveedores"],
        crud=crud.proveedor,
        read_schema=catalogo.ProveedorRead,
        create_schema=catalogo.ProveedorCreate,
        update_schema=catalogo.ProveedorUpdate,
        en_uso_msg="hay productos de este proveedor",
    )
)
api_router.include_router(
    make_crud_router(
        prefix="/productos",
        tags=["productos"],
        crud=crud.producto,
        read_schema=catalogo.ProductoRead,
        create_schema=catalogo.ProductoCreate,
        update_schema=catalogo.ProductoUpdate,
        en_uso_msg="hay lotes de este producto",
    )
)
# Vista calculada de lotes (antes del CRUD generico por prioridad de rutas).
api_router.include_router(lotes_vista.router)
api_router.include_router(
    make_crud_router(
        prefix="/lotes",
        tags=["lotes"],
        crud=crud.lote,
        read_schema=inventario.LoteRead,
        create_schema=inventario.LoteCreate,
        update_schema=inventario.LoteUpdate,
        en_uso_msg="hay existencias, inspecciones o alertas de este lote",
    )
)
api_router.include_router(
    make_crud_router(
        prefix="/inventario-lotes",
        tags=["inventario"],
        crud=crud.inventario_lote,
        read_schema=inventario.InventarioLoteRead,
        create_schema=inventario.InventarioLoteCreate,
        update_schema=inventario.InventarioLoteUpdate,
    )
)
# Registro de corta fecha: captura en un paso (producto + lote + inspeccion).
api_router.include_router(registros_corta_fecha.router)
api_router.include_router(inspecciones_vista.router)
api_router.include_router(
    make_crud_router(
        prefix="/inspecciones",
        tags=["inspecciones"],
        crud=crud.inspeccion,
        read_schema=operacion.InspeccionRead,
        create_schema=operacion.InspeccionCreate,
        update_schema=operacion.InspeccionUpdate,
    )
)
api_router.include_router(novedades_vista.router)
api_router.include_router(
    make_crud_router(
        prefix="/novedades",
        tags=["novedades"],
        crud=crud.novedad,
        read_schema=operacion.NovedadRead,
        create_schema=operacion.NovedadCreate,
        update_schema=operacion.NovedadUpdate,
    )
)

api_router.include_router(
    make_crud_router(
        prefix="/roles",
        tags=["roles"],
        crud=crud.rol,
        read_schema=auth.RolRead,
        create_schema=auth.RolCreate,
        update_schema=auth.RolUpdate,
        en_uso_msg="hay usuarios asignados a este rol",
    )
)

# Usuarios: router propio (hashing de contrasena).
api_router.include_router(usuarios.router)

# Alertas: router propio (sin create/delete; solo lectura + seguimiento).
api_router.include_router(alertas.router)

# Dashboard: indicadores agregados.
api_router.include_router(dashboard.router)

# Reportes y exportacion Excel.
api_router.include_router(reportes.router)

# Historial de cambios (auditoria) con paginacion en servidor.
api_router.include_router(historial.router)
