-- =====================================================================
-- Sistema Corta Fecha - Esquema de base de datos (PostgreSQL)
-- =====================================================================
-- Control de productos proximos a vencer y averiados.
-- Vencimiento controlado por LOTE. Existencias por LOTE + BODEGA.
--
-- Uso:
--   createdb corta_fecha
--   psql -d corta_fecha -f backend/db/schema.sql
--
-- Nota: este script es idempotente dentro de un esquema limpio.
-- Para produccion, versionar cambios con Alembic (no editar tablas en vivo).
-- =====================================================================

BEGIN;

-- Extension para claves UUID (opcional; aqui usamos BIGINT identity).
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================================
-- TIPOS ENUMERADOS
-- =====================================================================

-- Estado de alerta segun dias restantes hasta vencimiento.
CREATE TYPE estado_alerta AS ENUM (
    'normal',       -- mas de 90 dias
    'preventiva',   -- 61 a 90 dias
    'prioritaria',  -- 31 a 60 dias
    'critica',      -- 0 a 30 dias
    'vencido'       -- menos de 0 dias
);

-- Ciclo de vida del seguimiento de una alerta.
CREATE TYPE estado_seguimiento AS ENUM (
    'pendiente',
    'en_gestion',
    'gestionada',
    'descartada'
);

-- Tipo de movimiento de inventario.
CREATE TYPE tipo_movimiento AS ENUM (
    'entrada',
    'salida',
    'traslado',
    'ajuste'
);

-- Tipo de novedad / incidencia.
CREATE TYPE tipo_novedad AS ENUM (
    'averia',
    'rotura',
    'contaminacion',
    'empaque_danado',
    'otro'
);

-- Disposicion final de mercancia con novedad.
CREATE TYPE disposicion_novedad AS ENUM (
    'pendiente',
    'devolucion_proveedor',
    'baja',
    'donacion',
    'reproceso',
    'venta_descuento'
);

-- Estado de una accion de gestion.
CREATE TYPE estado_accion AS ENUM (
    'abierta',
    'en_progreso',
    'cerrada',
    'cancelada'
);

-- Accion registrada en auditoria.
CREATE TYPE accion_auditoria AS ENUM (
    'insert',
    'update',
    'delete'
);

-- =====================================================================
-- FUNCION: mantener updated_at
-- =====================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================================
-- SEGURIDAD: roles, permisos, usuarios
-- =====================================================================

CREATE TABLE roles (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE permisos (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    modulo      TEXT NOT NULL,      -- p.ej. 'inspecciones', 'alertas', 'reportes'
    accion      TEXT NOT NULL,      -- p.ej. 'ver', 'crear', 'editar', 'exportar'
    descripcion TEXT,
    UNIQUE (modulo, accion)
);

CREATE TABLE roles_permisos (
    rol_id     BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permiso_id BIGINT NOT NULL REFERENCES permisos(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

CREATE TABLE sucursales (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo     TEXT NOT NULL UNIQUE,
    nombre     TEXT NOT NULL,
    direccion  TEXT,
    activa     BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Bodegas pertenecen a una sucursal. Existencias se asocian a bodega.
CREATE TABLE bodegas (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sucursal_id  BIGINT NOT NULL REFERENCES sucursales(id) ON DELETE RESTRICT,
    codigo       TEXT NOT NULL,
    nombre       TEXT NOT NULL,
    activa       BOOLEAN NOT NULL DEFAULT true,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (sucursal_id, codigo)
);

CREATE TABLE usuarios (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    nombre        TEXT NOT NULL,
    password_hash TEXT NOT NULL,          -- hash seguro (argon2/bcrypt). Nunca texto plano.
    rol_id        BIGINT NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    sucursal_id   BIGINT REFERENCES sucursales(id) ON DELETE SET NULL, -- NULL = acceso a todas
    activo        BOOLEAN NOT NULL DEFAULT true,
    ultimo_acceso TIMESTAMPTZ,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);
CREATE INDEX idx_usuarios_sucursal ON usuarios(sucursal_id);

-- =====================================================================
-- CATALOGO: categorias, proveedores, productos
-- =====================================================================

CREATE TABLE categorias (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre      TEXT NOT NULL UNIQUE,
    descripcion TEXT,
    -- Umbrales de alerta ajustables por categoria. NULL = usar default global.
    dias_preventiva  INTEGER,
    dias_prioritaria INTEGER,
    dias_critica     INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proveedores (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre     TEXT NOT NULL,
    nit        TEXT UNIQUE,
    contacto   TEXT,
    telefono   TEXT,
    email      TEXT,
    activo     BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE productos (
    id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sku           TEXT NOT NULL UNIQUE,
    descripcion   TEXT NOT NULL,
    categoria_id  BIGINT REFERENCES categorias(id) ON DELETE SET NULL,
    proveedor_id  BIGINT REFERENCES proveedores(id) ON DELETE SET NULL,
    -- Unidad base de inventario (p.ej. 'unidad') y factor de empaque (unidades por caja).
    unidad_base   TEXT NOT NULL DEFAULT 'unidad',
    factor_empaque NUMERIC(12,3) NOT NULL DEFAULT 1 CHECK (factor_empaque > 0),
    activo        BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_productos_proveedor ON productos(proveedor_id);

-- =====================================================================
-- LOTES Y EXISTENCIAS
-- =====================================================================

-- Un producto puede tener varios lotes. Vencimiento vive aqui.
CREATE TABLE lotes (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    producto_id       BIGINT NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    numero_lote       TEXT NOT NULL,
    fecha_vencimiento DATE,            -- NULL permitido: lote sin fecha = dato inconsistente a revisar
    fecha_fabricacion DATE,
    activo            BOOLEAN NOT NULL DEFAULT true,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (producto_id, numero_lote)
);

CREATE INDEX idx_lotes_producto ON lotes(producto_id);
CREATE INDEX idx_lotes_vencimiento ON lotes(fecha_vencimiento);
-- Localiza rapido lotes sin fecha (datos a corregir).
CREATE INDEX idx_lotes_sin_fecha ON lotes(id) WHERE fecha_vencimiento IS NULL;

-- Existencia actual por lote + bodega (unidad base).
CREATE TABLE inventario_lotes (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id    BIGINT NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    bodega_id  BIGINT NOT NULL REFERENCES bodegas(id) ON DELETE RESTRICT,
    -- Total en unidades base; es la cifra que usan alertas y reportes.
    cantidad   NUMERIC(14,3) NOT NULL DEFAULT 0 CHECK (cantidad >= 0),
    -- Desglose declarado por el encargado (campos independientes, editables).
    -- NULL = no se declaro desglose y se deriva con productos.factor_empaque.
    cajas            NUMERIC(14,3) CHECK (cajas IS NULL OR cajas >= 0),
    unidades_sueltas NUMERIC(14,3) CHECK (unidades_sueltas IS NULL OR unidades_sueltas >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (lote_id, bodega_id)
);

CREATE INDEX idx_inv_lotes_bodega ON inventario_lotes(bodega_id);

-- Historico de movimientos que afectan existencias.
CREATE TABLE inventario_movimientos (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id        BIGINT NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    bodega_id      BIGINT NOT NULL REFERENCES bodegas(id) ON DELETE RESTRICT,
    tipo           tipo_movimiento NOT NULL,
    -- cantidad firmada: entrada/ajuste(+) positivo, salida negativo. Traslado = par salida+entrada.
    cantidad       NUMERIC(14,3) NOT NULL CHECK (cantidad <> 0),
    bodega_destino_id BIGINT REFERENCES bodegas(id) ON DELETE RESTRICT, -- solo traslado
    referencia     TEXT,      -- documento origen (venta, devolucion, orden)
    usuario_id     BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    observacion    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_mov_lote ON inventario_movimientos(lote_id);
CREATE INDEX idx_mov_bodega ON inventario_movimientos(bodega_id);
CREATE INDEX idx_mov_fecha ON inventario_movimientos(created_at);

-- =====================================================================
-- INSPECCIONES (captura fisica confirmada por usuario)
-- =====================================================================

CREATE TABLE inspecciones (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id            BIGINT NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    bodega_id          BIGINT NOT NULL REFERENCES bodegas(id) ON DELETE RESTRICT,
    responsable_id     BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    fecha_inspeccion   TIMESTAMPTZ NOT NULL DEFAULT now(),
    cantidad_contada   NUMERIC(14,3) CHECK (cantidad_contada >= 0),
    fecha_vencimiento_verificada DATE,   -- lo observado fisicamente
    observaciones      TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_insp_lote ON inspecciones(lote_id);
CREATE INDEX idx_insp_fecha ON inspecciones(fecha_inspeccion);
CREATE INDEX idx_insp_responsable ON inspecciones(responsable_id);

-- Evidencias (fotos/documentos) ligadas a una inspeccion.
CREATE TABLE inspeccion_evidencias (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    inspeccion_id  BIGINT NOT NULL REFERENCES inspecciones(id) ON DELETE CASCADE,
    url            TEXT NOT NULL,       -- ruta en S3 o almacenamiento interno
    tipo_mime      TEXT,
    descripcion    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_insp_evid_inspeccion ON inspeccion_evidencias(inspeccion_id);

-- =====================================================================
-- NOVEDADES / PRODUCTOS AVERIADOS
-- =====================================================================

CREATE TABLE novedades (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id            BIGINT NOT NULL REFERENCES lotes(id) ON DELETE RESTRICT,
    bodega_id          BIGINT NOT NULL REFERENCES bodegas(id) ON DELETE RESTRICT,
    inspeccion_id      BIGINT REFERENCES inspecciones(id) ON DELETE SET NULL,
    tipo               tipo_novedad NOT NULL,
    cantidad_afectada  NUMERIC(14,3) NOT NULL CHECK (cantidad_afectada > 0),
    disposicion        disposicion_novedad NOT NULL DEFAULT 'pendiente',
    reportado_por_id   BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    observaciones      TEXT,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_novedades_lote ON novedades(lote_id);
CREATE INDEX idx_novedades_tipo ON novedades(tipo);

CREATE TABLE novedad_evidencias (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    novedad_id   BIGINT NOT NULL REFERENCES novedades(id) ON DELETE CASCADE,
    url          TEXT NOT NULL,
    tipo_mime    TEXT,
    descripcion  TEXT,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_nov_evid_novedad ON novedad_evidencias(novedad_id);

-- =====================================================================
-- ALERTAS (calculadas por el proceso automatico)
-- =====================================================================
-- Una alerta NO prueba inspeccion fisica. Es calculo sobre lote+existencia.

CREATE TABLE alertas (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    lote_id            BIGINT NOT NULL REFERENCES lotes(id) ON DELETE CASCADE,
    sucursal_id        BIGINT NOT NULL REFERENCES sucursales(id) ON DELETE CASCADE,
    estado             estado_alerta NOT NULL,
    seguimiento        estado_seguimiento NOT NULL DEFAULT 'pendiente',
    dias_restantes     INTEGER,          -- al momento del calculo
    cantidad_en_riesgo NUMERIC(14,3),
    -- periodo de seguimiento para evitar duplicados (p.ej. '2026-11' o fecha corte).
    periodo            TEXT NOT NULL,
    calculada_en       TIMESTAMPTZ NOT NULL DEFAULT now(),
    actualizada_en     TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Evita alertas duplicadas para mismo lote + sucursal + periodo.
    UNIQUE (lote_id, sucursal_id, periodo)
);

CREATE INDEX idx_alertas_estado ON alertas(estado);
CREATE INDEX idx_alertas_seguimiento ON alertas(seguimiento);
CREATE INDEX idx_alertas_sucursal ON alertas(sucursal_id);

-- =====================================================================
-- GESTION DE ACCIONES (seguimiento / cierre de caso)
-- =====================================================================

CREATE TABLE acciones_gestion (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alerta_id      BIGINT REFERENCES alertas(id) ON DELETE SET NULL,
    novedad_id     BIGINT REFERENCES novedades(id) ON DELETE SET NULL,
    responsable_id BIGINT NOT NULL REFERENCES usuarios(id) ON DELETE RESTRICT,
    descripcion    TEXT NOT NULL,
    estado         estado_accion NOT NULL DEFAULT 'abierta',
    resultado      TEXT,
    fecha_limite   DATE,
    cerrada_en     TIMESTAMPTZ,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Debe referir a una alerta o a una novedad (al menos una).
    CHECK (alerta_id IS NOT NULL OR novedad_id IS NOT NULL)
);

CREATE INDEX idx_acciones_alerta ON acciones_gestion(alerta_id);
CREATE INDEX idx_acciones_novedad ON acciones_gestion(novedad_id);
CREATE INDEX idx_acciones_responsable ON acciones_gestion(responsable_id);

-- =====================================================================
-- AUDITORIA
-- =====================================================================

CREATE TABLE historial_cambios (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tabla       TEXT NOT NULL,
    registro_id BIGINT NOT NULL,
    accion      accion_auditoria NOT NULL,
    usuario_id  BIGINT REFERENCES usuarios(id) ON DELETE SET NULL,
    datos_antes JSONB,
    datos_despues JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_hist_tabla_registro ON historial_cambios(tabla, registro_id);
CREATE INDEX idx_hist_fecha ON historial_cambios(created_at);

-- Registro de ejecuciones del proceso de alertas (requisito 5.7).
CREATE TABLE alerta_ejecuciones (
    id               BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    iniciada_en      TIMESTAMPTZ NOT NULL DEFAULT now(),
    finalizada_en    TIMESTAMPTZ,
    lotes_evaluados  INTEGER,
    alertas_creadas  INTEGER,
    alertas_actualizadas INTEGER,
    lotes_sin_fecha  INTEGER,
    resultado        TEXT,      -- 'ok' | 'error' | detalle
    detalle          TEXT
);

-- =====================================================================
-- TRIGGERS updated_at
-- =====================================================================
CREATE TRIGGER trg_roles_upd        BEFORE UPDATE ON roles             FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_sucursales_upd   BEFORE UPDATE ON sucursales        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_bodegas_upd      BEFORE UPDATE ON bodegas           FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_usuarios_upd     BEFORE UPDATE ON usuarios          FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_categorias_upd   BEFORE UPDATE ON categorias        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_proveedores_upd  BEFORE UPDATE ON proveedores       FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_productos_upd    BEFORE UPDATE ON productos         FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_lotes_upd        BEFORE UPDATE ON lotes             FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_inv_lotes_upd    BEFORE UPDATE ON inventario_lotes  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_novedades_upd    BEFORE UPDATE ON novedades         FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_acciones_upd     BEFORE UPDATE ON acciones_gestion  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

COMMIT;

-- =====================================================================
-- FIN DEL ESQUEMA
-- =====================================================================
