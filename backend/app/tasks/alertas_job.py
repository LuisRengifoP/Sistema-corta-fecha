"""Job de calculo de alertas para tarea programada.

MVP: invocar manual o via cron/scheduler simple:
    python -m app.tasks.alertas_job

Fase 2: envolver en una tarea Celery + Celery Beat (ver docs/arquitectura.md).
"""

from datetime import datetime, timezone

from app.core.database import SessionLocal
from app.models.auditoria import AlertaEjecucion
from app.services.alertas import calcular_alertas


def ejecutar() -> dict:
    db = SessionLocal()
    ejec = AlertaEjecucion()
    db.add(ejec)
    db.commit()
    db.refresh(ejec)
    try:
        r = calcular_alertas(db)
        ejec.finalizada_en = datetime.now(timezone.utc)
        ejec.lotes_evaluados = r.lotes_evaluados
        ejec.alertas_creadas = r.alertas_creadas
        ejec.alertas_actualizadas = r.alertas_actualizadas
        ejec.lotes_sin_fecha = r.lotes_sin_fecha
        ejec.resultado = "ok"
        db.commit()
        return {
            "lotes_evaluados": r.lotes_evaluados,
            "alertas_creadas": r.alertas_creadas,
            "alertas_actualizadas": r.alertas_actualizadas,
            "lotes_sin_fecha": r.lotes_sin_fecha,
        }
    except Exception as exc:  # noqa: BLE001
        ejec.finalizada_en = datetime.now(timezone.utc)
        ejec.resultado = "error"
        ejec.detalle = str(exc)
        db.commit()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print(ejecutar())
