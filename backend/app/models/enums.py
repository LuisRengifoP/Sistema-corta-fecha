import enum


class EstadoAlerta(str, enum.Enum):
    normal = "normal"
    preventiva = "preventiva"
    prioritaria = "prioritaria"
    critica = "critica"
    vencido = "vencido"


class EstadoSeguimiento(str, enum.Enum):
    pendiente = "pendiente"
    en_gestion = "en_gestion"
    gestionada = "gestionada"
    descartada = "descartada"


class TipoMovimiento(str, enum.Enum):
    entrada = "entrada"
    salida = "salida"
    traslado = "traslado"
    ajuste = "ajuste"


class TipoNovedad(str, enum.Enum):
    averia = "averia"
    rotura = "rotura"
    contaminacion = "contaminacion"
    empaque_danado = "empaque_danado"
    otro = "otro"


class DisposicionNovedad(str, enum.Enum):
    pendiente = "pendiente"
    devolucion_proveedor = "devolucion_proveedor"
    baja = "baja"
    donacion = "donacion"
    reproceso = "reproceso"
    venta_descuento = "venta_descuento"


class EstadoAccion(str, enum.Enum):
    abierta = "abierta"
    en_progreso = "en_progreso"
    cerrada = "cerrada"
    cancelada = "cancelada"


class AccionAuditoria(str, enum.Enum):
    insert = "insert"
    update = "update"
    delete = "delete"
