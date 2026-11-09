# Arquitectura

## Vision general

Aplicacion web de tres capas:

```
[ SvelteKit (frontend) ]  --HTTP/JSON-->  [ FastAPI (backend) ]  -->  [ PostgreSQL ]
                                                 |
                                                 +--> Almacenamiento evidencias (local / S3)
                                                 +--> (futuro) Celery + Redis
```

## Componentes

| Componente | Tecnologia | Responsabilidad |
|-----------|-----------|-----------------|
| Frontend  | SvelteKit + TS + Tailwind | UI, navegacion, dashboard, formularios |
| Backend   | FastAPI + SQLAlchemy 2.x  | API REST, reglas de negocio, validaciones, auth JWT |
| Base datos| PostgreSQL | Productos, lotes, existencias, inspecciones, alertas, usuarios |
| Migraciones | Alembic | Versionado de esquema |
| Tareas    | Celery + Celery Beat + Redis | Revision periodica y generacion de alertas (fase 2) |
| Excel     | Pandas + OpenPyXL | Exportacion de reportes |
| Despliegue| Docker + Docker Compose | Orquestacion de servicios |
| Proxy     | Nginx | HTTPS y enrutamiento (produccion) |

## Principios

- Backend independiente via API REST (reutilizable para movil/escritorio futuros).
- Separacion de ambientes: desarrollo / pruebas / produccion.
- Validacion en frontend y backend.
- Secretos por variables de entorno; nunca en el repositorio.

## Entornos

- **Local:** `docker compose up` levanta db, redis, backend, frontend.
- **Pruebas / produccion:** mismos contenedores detras de Nginx con HTTPS,
  Postgres gestionado o con backups automaticos.
