"""Carga los proveedores reales tomados del reporte STOCK X PROVEEDOR X BODEGA.

Uso:
    cd backend
    python -m scripts.seed_proveedores

Idempotente: omite los proveedores cuyo nombre ya existe.
"""

from app.core.database import SessionLocal
from app.models.catalogo import Proveedor

PROVEEDORES = [
    "PROVEEDORES (OFERTAS Y VARIOS)",
    "PERNOD RICARD COLOMBIA S.A.",
    "MASTERFOODS COLOMBIA LTDA EFFEM COLOMBIA",
    "TEAM FOODS COLOMBIA S.A.",
    "UNILEVER ANDINA COLOMBIA LTDA",
    "GRADEZCO LTDA",
    "COLOMBIANA KIMBERLY COLPAPEL S.A.S.",
    "QUALA S.A.",
    "COLGATE PALMOLIVE COMPAÑIA",
    "DISTRIBUIDORA COLOMBINA LTDA",
    "TRIGUISAR DE COLOMBIA S.A.",
    "BRITISH AMERICAN TOBACCO COLOMBIA S.A.S.",
    "HALEON COLOMBIA S.A.S.",
    "C.I. SUPER S.A.S.",
    "COLPAPEL TISSUE S.A.S",
]


def main() -> None:
    db = SessionLocal()
    try:
        existentes = {p.nombre for p in db.query(Proveedor).all()}
        creados = 0
        for nombre in PROVEEDORES:
            if nombre in existentes:
                print(f"- Ya existe: {nombre}")
                continue
            db.add(Proveedor(nombre=nombre))
            creados += 1
            print(f"+ Creado:   {nombre}")
        db.commit()
        print(f"\nTotal creados: {creados} / {len(PROVEEDORES)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
