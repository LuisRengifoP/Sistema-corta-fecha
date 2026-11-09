# Modelo de datos

Esquema de referencia: [`backend/db/schema.sql`](../backend/db/schema.sql).

## Reglas de modelado

- El vencimiento se controla por **lote**, no por SKU.
- Las existencias se asocian a **lote + bodega** (`inventario_lotes`).
- Unidad base de inventario + `factor_empaque` para convertir caja <-> unidad.
- Movimientos (`inventario_movimientos`): entrada, salida, traslado, ajuste.
- Historial de inspecciones y cambios conservado; no se sobrescribe sin auditoria.
- Sin alertas duplicadas: `UNIQUE (lote_id, sucursal_id, periodo)` en `alertas`.
- Una **alerta** (calculada) no equivale a una **inspeccion** (confirmada por usuario).

## Tablas

| Tabla | Proposito |
|-------|-----------|
| `roles`, `permisos`, `roles_permisos` | Perfiles y permisos por modulo/accion |
| `usuarios` | Usuarios, con `rol_id` y `sucursal_id` |
| `sucursales`, `bodegas` | Ubicaciones fisicas (bodega pertenece a sucursal) |
| `categorias` | Categorias + umbrales de alerta ajustables |
| `proveedores` | Proveedores |
| `productos` | Maestro SKU, unidad base, factor de empaque |
| `lotes` | Numero de lote y fecha de vencimiento |
| `inventario_lotes` | Existencia por lote + bodega |
| `inventario_movimientos` | Entradas/salidas/traslados/ajustes |
| `inspecciones`, `inspeccion_evidencias` | Revision fisica + fotos/documentos |
| `novedades`, `novedad_evidencias` | Productos averiados e incidencias |
| `alertas` | Alertas calculadas por estado y periodo |
| `acciones_gestion` | Acciones correctivas y cierre de caso |
| `historial_cambios` | Auditoria de modificaciones (JSONB antes/despues) |
| `alerta_ejecuciones` | Bitacora de cada corrida del proceso de alertas |

## Enums

- `estado_alerta`: normal, preventiva, prioritaria, critica, vencido
- `estado_seguimiento`: pendiente, en_gestion, gestionada, descartada
- `tipo_movimiento`: entrada, salida, traslado, ajuste
- `tipo_novedad`: averia, rotura, contaminacion, empaque_danado, otro
- `disposicion_novedad`: pendiente, devolucion_proveedor, baja, donacion, reproceso, venta_descuento
- `estado_accion`: abierta, en_progreso, cerrada, cancelada
- `accion_auditoria`: insert, update, delete
