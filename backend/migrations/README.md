# Migraciones (Alembic)

El esquema de referencia esta en `backend/db/schema.sql`.

Para versionar cambios con Alembic:

```bash
cd backend
alembic init migrations          # genera alembic.ini + env.py (una sola vez)
alembic revision --autogenerate -m "inicial"
alembic upgrade head
```

En `env.py` apuntar `target_metadata = Base.metadata` (ver `app/core/database.py`)
y tomar la URL de `app.core.config.get_settings().DATABASE_URL`.
