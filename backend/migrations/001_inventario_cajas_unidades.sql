-- Migracion 001: desglose explicito de cajas y unidades sueltas.
--
-- Problema: la vista de lotes derivaba el desglose con
-- productos.factor_empaque. Como el registro de corta fecha creaba los
-- productos con factor_empaque = 1, una captura de 214 unidades se mostraba
-- como "214 cajas + 0 unidades".
--
-- Solucion: guardar el desglose que declara el encargado. Ambas columnas son
-- independientes y admiten NULL (sin desglose declarado: se sigue derivando
-- con factor_empaque, igual que antes).
--
-- Aplicar con:
--   psql "$DATABASE_URL" -f migrations/001_inventario_cajas_unidades.sql

BEGIN;

ALTER TABLE inventario_lotes
    ADD COLUMN IF NOT EXISTS cajas            NUMERIC(14,3),
    ADD COLUMN IF NOT EXISTS unidades_sueltas NUMERIC(14,3);

ALTER TABLE inventario_lotes
    DROP CONSTRAINT IF EXISTS inventario_lotes_cajas_check,
    DROP CONSTRAINT IF EXISTS inventario_lotes_unidades_sueltas_check;

ALTER TABLE inventario_lotes
    ADD CONSTRAINT inventario_lotes_cajas_check
        CHECK (cajas IS NULL OR cajas >= 0),
    ADD CONSTRAINT inventario_lotes_unidades_sueltas_check
        CHECK (unidades_sueltas IS NULL OR unidades_sueltas >= 0);

COMMIT;
