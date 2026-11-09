# Herramientas y tecnologías --- Sistema Corta Fecha

**Objetivo:** definir el stack tecnológico y las herramientas necesarias
para desarrollar una plataforma web que controle productos próximos a
vencer y averiados, gestione lotes e inspecciones, genere alertas y
exporte informes a Excel.

## 1. Stack tecnológico recomendado

  -----------------------------------------------------------------------
  Capa                    Herramienta             Uso
  ----------------------- ----------------------- -----------------------
  Frontend                **SvelteKit**           Aplicación web,
                                                  navegación y
                                                  renderizado de páginas

  Lenguaje frontend       **TypeScript**          Tipado, mantenibilidad
                                                  y reducción de errores

  Estilos                 **Tailwind CSS**        Diseño adaptable y
                                                  sistema visual

  Componentes UI          **Skeleton UI** o       Formularios, diálogos,
                          componentes propios     menús y elementos de
                                                  interfaz

  Iconos                  **Lucide Svelte**       Iconografía consistente

  Tablas                  **TanStack Table para   Tablas con filtros,
                          Svelte**                ordenamiento y
                                                  paginación

  Gráficos                **LayerChart** o        Indicadores y
                          **Chart.js**            estadísticas del
                                                  dashboard

  Backend                 **Python + FastAPI**    API REST, reglas de
                                                  negocio y validaciones

  ORM / acceso a datos    **SQLAlchemy 2.x**      Consultas y relaciones
                                                  con PostgreSQL

  Migraciones             **Alembic**             Crear y versionar
                                                  cambios en la
                                                  estructura de la base
                                                  de datos

  Base de datos           **PostgreSQL**          Productos, lotes,
                                                  existencias,
                                                  inspecciones, alertas y
                                                  usuarios

  Tareas programadas      **Celery + Celery       Revisiones periódicas y
                          Beat**                  generación programada
                                                  de alertas

  Cola / intermediario    **Redis**               Cola de tareas y
                                                  coordinación de
                                                  procesos asíncronos

  Excel                   **Pandas + OpenPyXL**   Lectura, generación y
                                                  formato de archivos
                                                  Excel

  Archivos y evidencias   Almacenamiento          Fotografías, documentos
                          compatible con S3 o     y evidencias de
                          almacenamiento interno  inspección

  Autenticación           JWT mediante FastAPI    Inicio de sesión y
                                                  autorización

  Despliegue              **Docker + Docker       Ejecutar frontend,
                          Compose**               backend, base de datos
                                                  y servicios

  Servidor web / proxy    **Nginx** o proxy       HTTPS y enrutamiento
                          administrado            hacia los servicios
  -----------------------------------------------------------------------

> Para una primera versión pequeña, Celery y Redis pueden aplazarse: las
> alertas pueden ejecutarse con una tarea programada sencilla. Se
> incorporan cuando se necesiten colas, reintentos o mayor volumen de
> procesamiento.

## 2. Herramientas de desarrollo

  -----------------------------------------------------------------------
  Herramienta                         Uso
  ----------------------------------- -----------------------------------
  **Visual Studio Code**              Editor principal de código

  **Git**                             Control de versiones

  **GitHub o GitLab**                 Repositorio, ramas, revisión de
                                      cambios y seguimiento

  **Postman** o **Insomnia**          Probar endpoints de la API

  **DBeaver** o **pgAdmin**           Administrar y consultar PostgreSQL

  **Figma**                           Diseñar prototipos y definir la
                                      experiencia de usuario

  **Docker Desktop**                  Ejecutar el entorno local mediante
                                      contenedores

  **Swagger UI / OpenAPI**            Consultar y probar la documentación
                                      automática de FastAPI

  **Prettier + ESLint**               Formato y revisión del código
                                      frontend

  **Ruff + pytest**                   Calidad de código y pruebas del
                                      backend
  -----------------------------------------------------------------------

## 3. Módulos que debe soportar la solución

1.  **Dashboard:** indicadores de lotes próximos a vencer, vencidos,
    averiados, pendientes y gestionados.
2.  **Productos e inventario:** consulta de SKU, descripción, categoría,
    proveedor, sucursal y existencias.
3.  **Lotes y vencimientos:** fecha de vencimiento, lote, cantidades y
    ubicación física. Un producto puede tener varios lotes.
4.  **Inspecciones:** captura física de lote, fecha, cantidades,
    fotografías, observaciones y responsable.
5.  **Alertas:** clasificación por días restantes, notificaciones y
    seguimiento de cada alerta.
6.  **Productos averiados:** registro de daños, cantidades afectadas,
    evidencias y disposición.
7.  **Gestión de acciones:** asignación de responsables, acciones
    correctivas y cierre del caso.
8.  **Reportes:** filtros y exportación a Excel.
9.  **Usuarios y permisos:** roles, sucursales y permisos por módulo.
10. **Auditoría:** historial de cambios, inspecciones, alertas y
    acciones realizadas.

## 4. Estructura inicial de la base de datos

Tablas recomendadas:

  Tabla                 Propósito
  --------------------- ------------------------------------------------
  `usuarios`            Usuarios del sistema
  `roles`               Perfiles de acceso
  `permisos`            Permisos por módulo y acción
  `sucursales`          Sucursales y bodegas
  `productos`           Maestro de productos y SKU
  `categorias`          Categorías de productos
  `proveedores`         Proveedores
  `lotes`               Identificación del lote y fecha de vencimiento
  `inventario_lotes`    Existencias por lote y bodega
  `inspecciones`        Revisiones físicas
  `novedades`           Productos averiados y otras incidencias
  `alertas`             Alertas generadas
  `acciones_gestion`    Acciones y resultados de gestión
  `historial_cambios`   Auditoría de modificaciones

**Reglas de modelado importantes:**

-   El vencimiento se controla por lote, no solamente por SKU.
-   Las existencias deben asociarse al lote y a la bodega o sucursal.
-   Definir una unidad base de inventario y el factor de empaque para
    convertir entre cajas y unidades.
-   Registrar movimientos de entrada, salida, traslado y ajuste para
    mantener las existencias actualizadas.
-   Conservar el historial de inspecciones y cambios; no sobrescribir
    datos importantes sin auditoría.
-   Evitar alertas duplicadas para el mismo lote, sucursal y periodo de
    seguimiento.

## 5. Reglas de negocio y alertas

Como configuración inicial ---ajustable por categoría--- se propone:

  Estado           Días restantes
  ------------- -----------------
  Normal           Más de 90 días
  Preventiva         61 a 90 días
  Prioritaria        31 a 60 días
  Crítica             0 a 30 días
  Vencido         Menos de 0 días

El proceso automático debe:

1.  Consultar lotes activos y existencias.
2.  Calcular los días restantes hasta el vencimiento.
3.  Clasificar cada lote según los umbrales configurados.
4.  Crear o actualizar alertas sin duplicarlas.
5.  Notificar a los responsables correspondientes.
6.  Detectar lotes sin fecha o con datos inconsistentes.
7.  Registrar la fecha y el resultado de cada ejecución.

**Importante:** una alerta no demuestra por sí sola que el producto fue
inspeccionado físicamente. El sistema debe distinguir entre una alerta
calculada y una inspección confirmada por un usuario.

## 6. Integraciones y datos de origen

Antes de desarrollar la automatización, confirmar qué información
entrega el sistema actual de inventario.

**Datos mínimos necesarios:**

-   SKU o código del producto.
-   Descripción.
-   Sucursal y bodega.
-   Existencia.
-   Unidad de medida.
-   Factor de empaque.
-   Número de lote.
-   Fecha de vencimiento.

Si el sistema actual no almacena lote y vencimiento, estos datos deberán
capturarse durante la inspección física. No es posible deducir de forma
confiable la fecha de vencimiento únicamente a partir del SKU.

Definir también cómo se sincronizarán ventas, traslados, devoluciones,
bajas y ajustes para que las cantidades de cada lote no queden
desactualizadas.

## 7. Seguridad, calidad y operación

-   Autenticación segura y permisos por rol y sucursal.
-   Contraseñas almacenadas mediante hash seguro.
-   Validación de datos tanto en frontend como en backend.
-   HTTPS en producción.
-   Copias de seguridad automáticas de PostgreSQL y pruebas de
    restauración.
-   Registro de errores y eventos relevantes.
-   Pruebas unitarias de reglas de vencimiento y cálculos de inventario.
-   Pruebas de integración de API y base de datos.
-   Pruebas de exportación Excel con grandes volúmenes.
-   Política de retención y acceso a fotografías y documentos.
-   Separación de ambientes de desarrollo, pruebas y producción.

## 8. Estructura sugerida del repositorio

``` text
corta-fecha/
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   ├── stores/
│   │   │   ├── types/
│   │   │   └── utils/
│   │   └── routes/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   └── main.py
│   ├── migrations/
│   └── requirements.txt
│
├── docs/
│   ├── arquitectura.md
│   ├── modelo_datos.md
│   └── reglas_negocio.md
│
├── docker-compose.yml
└── README.md
```

## 9. Orden recomendado de implementación

  -----------------------------------------------------------------------
  Etapa                               Entregable
  ----------------------------------- -----------------------------------
  1\. Levantamiento                   Fuente de inventario, proceso
                                      actual y responsables identificados

  2\. Diseño                          Prototipo de interfaz, arquitectura
                                      y modelo entidad-relación

  3\. Base de datos                   Tablas, relaciones, restricciones y
                                      migraciones

  4\. Backend                         API de productos, lotes,
                                      existencias, inspecciones y
                                      usuarios

  5\. Frontend                        Inicio de sesión, dashboard y
                                      módulos operativos

  6\. Alertas                         Cálculo de vencimientos,
                                      notificaciones y seguimiento

  7\. Reportes                        Filtros y exportación Excel

  8\. Integración                     Sincronización con inventario de la
                                      empresa

  9\. Pruebas y despliegue            Validación operativa, seguridad,
                                      capacitación y puesta en marcha
  -----------------------------------------------------------------------

## 10. Alcance recomendado para la primera versión (MVP)

Para evitar que el proyecto crezca demasiado antes de validar el
proceso, la primera versión debería incluir:

-   Inicio de sesión y roles básicos.
-   Importación o sincronización del inventario.
-   Registro de productos, lotes, vencimientos y cantidades.
-   Inspección física con responsable y observaciones.
-   Dashboard con clasificación de vencimientos.
-   Alertas automáticas.
-   Exportación de resultados a Excel.
-   Historial de inspecciones y cambios.

En una segunda etapa se pueden incorporar lectura de códigos de barras,
fotografías, notificaciones avanzadas, análisis de riesgo económico e
integración más profunda con otros sistemas empresariales.

## 11. Decisiones que deben confirmarse antes de programar

-   ¿De qué sistema o archivo se obtendrá el inventario?
-   ¿La fuente actual contiene lotes y fechas de vencimiento?
-   ¿Cuántas bodegas y sucursales participarán?
-   ¿Quién registra las inspecciones y quién aprueba la gestión?
-   ¿Las alertas se enviarán por correo, dentro del sistema o por ambos
    medios?
-   ¿Qué acciones se permiten para mercancía próxima a vencer o
    averiada?
-   ¿Qué volumen aproximado de productos y lotes se manejará?

**Recomendación final:** comenzar con SvelteKit + TypeScript en el
frontend, FastAPI en el backend y PostgreSQL como base de datos.
Mantener el backend independiente mediante API REST permitirá reutilizar
la lógica si más adelante se desarrolla una aplicación móvil o de
escritorio.
