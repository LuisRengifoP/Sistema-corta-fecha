# Reglas de negocio y alertas

## Clasificacion por dias restantes

Configuracion inicial (ajustable por categoria via `categorias.dias_*`):

| Estado | Dias restantes |
|--------|----------------|
| Normal | Mas de 90 dias |
| Preventiva | 61 a 90 dias |
| Prioritaria | 31 a 60 dias |
| Critica | 0 a 30 dias |
| Vencido | Menos de 0 dias |

## Proceso automatico de alertas

1. Consultar lotes activos y existencias.
2. Calcular dias restantes hasta el vencimiento.
3. Clasificar cada lote segun los umbrales configurados.
4. Crear o actualizar alertas sin duplicarlas (`lote_id + sucursal_id + periodo`).
5. Notificar a los responsables.
6. Detectar lotes sin fecha o con datos inconsistentes.
7. Registrar fecha y resultado de cada ejecucion (`alerta_ejecuciones`).

## Importante

- Una alerta es un **calculo**; no prueba inspeccion fisica.
- El sistema distingue alerta calculada vs inspeccion confirmada por usuario.
- La fecha de vencimiento no se deduce del SKU: si la fuente no la trae,
  se captura en la inspeccion fisica.

## Datos minimos de la fuente de inventario

SKU, descripcion, sucursal, bodega, existencia, unidad de medida,
factor de empaque, numero de lote, fecha de vencimiento.

Definir sincronizacion de ventas, traslados, devoluciones, bajas y ajustes
para mantener las cantidades por lote actualizadas.
