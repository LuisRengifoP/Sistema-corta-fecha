from __future__ import annotations

import io
from datetime import date, datetime, timezone
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.catalogo import Producto
from app.models.inventario import Lote
from app.models.operacion import Inspeccion, Novedad
from app.models.seguridad import Bodega, Sucursal, Usuario
from app.services.lotes import listar_vista

# Columnas por reporte: (clave, etiqueta).
COLUMNAS: dict[str, list[tuple[str, str]]] = {
    "lotes": [
        ("producto_sku", "SKU"),
        ("producto_descripcion", "Producto"),
        ("numero_lote", "Lote"),
        ("fecha_vencimiento", "Vencimiento"),
        ("dias_restantes", "Dias restantes"),
        ("existencia_total", "Existencia"),
        ("n_bodegas", "Bodegas"),
        ("estado", "Estado"),
    ],
    "inspecciones": [
        ("fecha_inspeccion", "Fecha"),
        ("producto_sku", "SKU"),
        ("producto_descripcion", "Producto"),
        ("numero_lote", "Lote"),
        ("bodega_nombre", "Bodega"),
        ("responsable", "Responsable"),
        ("cantidad_contada", "Contado"),
    ],
    "averiados": [
        ("created_at", "Fecha"),
        ("producto_sku", "SKU"),
        ("producto_descripcion", "Producto"),
        ("numero_lote", "Lote"),
        ("tipo", "Tipo"),
        ("cantidad_afectada", "Afectada"),
        ("bodega_nombre", "Bodega"),
        ("disposicion", "Disposicion"),
    ],
}

TITULOS = {
    "lotes": "Lotes por vencimiento",
    "inspecciones": "Inspecciones realizadas",
    "averiados": "Productos averiados",
}


def _filas_lotes(db: Session, filtros: dict) -> list[dict]:
    return listar_vista(
        db,
        q=filtros.get("q"),
        estado=filtros.get("estado"),
        sucursal_id=filtros.get("sucursal_id"),
    )


def _filas_inspecciones(db: Session, filtros: dict) -> list[dict]:
    rows = db.execute(
        select(
            Inspeccion.fecha_inspeccion,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Bodega.nombre,
            Usuario.nombre,
            Inspeccion.cantidad_contada,
        )
        .join(Lote, Lote.id == Inspeccion.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Bodega, Bodega.id == Inspeccion.bodega_id)
        .join(Usuario, Usuario.id == Inspeccion.responsable_id)
        .order_by(Inspeccion.fecha_inspeccion.desc())
    ).all()
    return [
        {
            "fecha_inspeccion": r[0],
            "producto_sku": r[1],
            "producto_descripcion": r[2],
            "numero_lote": r[3],
            "bodega_nombre": r[4],
            "responsable": r[5],
            "cantidad_contada": r[6],
        }
        for r in rows
    ]


def _filas_averiados(db: Session, filtros: dict) -> list[dict]:
    stmt = (
        select(
            Novedad.created_at,
            Producto.sku,
            Producto.descripcion,
            Lote.numero_lote,
            Novedad.tipo,
            Novedad.cantidad_afectada,
            Bodega.nombre,
            Novedad.disposicion,
        )
        .join(Lote, Lote.id == Novedad.lote_id)
        .join(Producto, Producto.id == Lote.producto_id)
        .join(Bodega, Bodega.id == Novedad.bodega_id)
        .order_by(Novedad.created_at.desc())
    )
    if filtros.get("disposicion"):
        stmt = stmt.where(Novedad.disposicion == filtros["disposicion"])
    return [
        {
            "created_at": r[0],
            "producto_sku": r[1],
            "producto_descripcion": r[2],
            "numero_lote": r[3],
            "tipo": r[4].value,
            "cantidad_afectada": r[5],
            "bodega_nombre": r[6],
            "disposicion": r[7].value,
        }
        for r in db.execute(stmt).all()
    ]


_BUILDERS = {
    "lotes": _filas_lotes,
    "inspecciones": _filas_inspecciones,
    "averiados": _filas_averiados,
}


def _resumen(tipo: str, filas: list[dict]) -> dict[str, int | str]:
    if tipo == "lotes":
        r: dict[str, int | str] = {"Total lotes": len(filas)}
        for est in ("vencido", "critica", "prioritaria", "preventiva", "normal", "sin_fecha"):
            r[est] = sum(1 for f in filas if f["estado"] == est)
        return r
    if tipo == "inspecciones":
        return {"Total inspecciones": len(filas)}
    if tipo == "averiados":
        total_afectada = sum((Decimal(str(f["cantidad_afectada"])) for f in filas), Decimal(0))
        return {"Total casos": len(filas), "Cantidad afectada": float(total_afectada)}
    return {"Total": len(filas)}


def construir(db: Session, tipo: str, filtros: dict) -> dict:
    if tipo not in _BUILDERS:
        raise ValueError(f"Reporte desconocido: {tipo}")
    filas = _BUILDERS[tipo](db, filtros)
    return {
        "tipo": tipo,
        "titulo": TITULOS[tipo],
        "columnas": [{"clave": k, "etiqueta": e} for k, e in COLUMNAS[tipo]],
        "filas": filas,
        "resumen": _resumen(tipo, filas),
    }


def _fmt(valor) -> object:
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, Decimal):
        return float(valor)
    return valor if valor is not None else ""


def exportar_excel(db: Session, tipo: str, filtros: dict) -> bytes:
    datos = construir(db, tipo, filtros)
    columnas = COLUMNAS[tipo]
    generado = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    params = ", ".join(f"{k}={v}" for k, v in filtros.items() if v not in (None, "")) or "ninguno"

    wb = Workbook()
    azul = PatternFill("solid", fgColor="172B4D")
    blanco = Font(color="FFFFFF", bold=True)

    # Hoja Resumen
    ws = wb.active
    ws.title = "Resumen"
    ws["A1"] = datos["titulo"]
    ws["A1"].font = Font(size=14, bold=True)
    ws["A2"] = f"Generado: {generado}"
    ws["A3"] = f"Parametros: {params}"
    fila = 5
    ws.cell(fila, 1, "Indicador").font = Font(bold=True)
    ws.cell(fila, 2, "Valor").font = Font(bold=True)
    for k, v in datos["resumen"].items():
        fila += 1
        ws.cell(fila, 1, str(k))
        ws.cell(fila, 2, v)
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 18

    # Hoja Detalle
    wd = wb.create_sheet("Detalle")
    for col, (_clave, etiqueta) in enumerate(columnas, start=1):
        c = wd.cell(1, col, etiqueta)
        c.fill = azul
        c.font = blanco
        c.alignment = Alignment(horizontal="center")
    for i, f in enumerate(datos["filas"], start=2):
        for col, (clave, _etiqueta) in enumerate(columnas, start=1):
            wd.cell(i, col, _fmt(f.get(clave)))
    for col in range(1, len(columnas) + 1):
        wd.column_dimensions[get_column_letter(col)].width = 20
    wd.freeze_panes = "A2"

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
