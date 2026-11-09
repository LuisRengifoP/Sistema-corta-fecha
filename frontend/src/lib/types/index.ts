export type EstadoAlerta =
  | 'normal'
  | 'preventiva'
  | 'prioritaria'
  | 'critica'
  | 'vencido';

export type EstadoSeguimiento =
  | 'pendiente'
  | 'en_gestion'
  | 'gestionada'
  | 'descartada';

export interface Usuario {
  id: number;
  email: string;
  nombre: string;
  rol_id: number;
  sucursal_id: number | null;
  activo: boolean;
  ultimo_acceso: string | null;
}

export interface ResumenDashboard {
  alertas_por_estado: Record<EstadoAlerta, number>;
  alertas_por_seguimiento: Record<EstadoSeguimiento, number>;
  total_alertas: number;
  total_productos: number;
  total_lotes: number;
  lotes_sin_fecha: number;
}

/** estado de lote: EstadoAlerta + 'sin_fecha'. */
export type EstadoLote = EstadoAlerta | 'sin_fecha';

export interface LoteVistaRow {
  id: number;
  producto_id: number;
  producto_sku: string;
  producto_descripcion: string;
  numero_lote: string;
  fecha_vencimiento: string | null;
  dias_restantes: number | null;
  existencia_total: string;
  cajas: number;
  unidades: string;
  n_bodegas: number;
  estado: EstadoLote;
  ultima_inspeccion: string | null;
}

export interface ExistenciaBodega {
  bodega_id: number;
  bodega_nombre: string;
  sucursal_nombre: string;
  cantidad: string;
}

export interface InspeccionResumen {
  id: number;
  fecha_inspeccion: string;
  responsable: string;
  cantidad_contada: string | null;
  observaciones: string | null;
}

export interface AlertaVistaRow {
  id: number;
  lote_id: number;
  producto_sku: string;
  producto_descripcion: string;
  numero_lote: string;
  sucursal_nombre: string;
  estado: EstadoAlerta;
  seguimiento: EstadoSeguimiento;
  dias_restantes: number | null;
  cantidad_en_riesgo: string | null;
  calculada_en: string;
  responsable: string | null;
  tiene_inspeccion: boolean;
}

export interface InspeccionVistaRow {
  id: number;
  producto_sku: string;
  producto_descripcion: string;
  numero_lote: string;
  bodega_nombre: string;
  fecha_inspeccion: string;
  responsable: string;
  cantidad_contada: string | null;
  observaciones: string | null;
}

export type TipoNovedad =
  | 'averia'
  | 'rotura'
  | 'contaminacion'
  | 'empaque_danado'
  | 'otro';

export type DisposicionNovedad =
  | 'pendiente'
  | 'devolucion_proveedor'
  | 'baja'
  | 'donacion'
  | 'reproceso'
  | 'venta_descuento';

export interface NovedadVistaRow {
  id: number;
  lote_id: number;
  producto_sku: string;
  producto_descripcion: string;
  numero_lote: string;
  bodega_nombre: string;
  tipo: TipoNovedad;
  cantidad_afectada: string;
  disposicion: DisposicionNovedad;
  reportado_por: string;
  created_at: string;
}

export interface NovedadResumen {
  total: number;
  abiertas: number;
  cerradas: number;
  cantidad_afectada: string;
  por_disposicion: Record<DisposicionNovedad, number>;
}

export interface LoteDetalle {
  id: number;
  producto_sku: string;
  producto_descripcion: string;
  categoria: string | null;
  proveedor: string | null;
  unidad_base: string;
  factor_empaque: string;
  numero_lote: string;
  fecha_vencimiento: string | null;
  fecha_fabricacion: string | null;
  dias_restantes: number | null;
  estado: EstadoLote;
  existencia_total: string;
  existencias: ExistenciaBodega[];
  inspecciones: InspeccionResumen[];
}
