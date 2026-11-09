# Sistema Corta Fecha

Plataforma web para controlar productos proximos a vencer y averiados:
gestion de lotes, inspecciones fisicas, alertas automaticas y reportes Excel.

## Stack

- **Frontend:** SvelteKit + TypeScript + Tailwind CSS
- **Backend:** Python + FastAPI + SQLAlchemy 2.x + Alembic
- **Base de datos:** PostgreSQL
- **Tareas programadas:** Celery + Redis (diferido para el MVP)
- **Excel:** Pandas + OpenPyXL
- **Despliegue:** Docker + Docker Compose

## Estructura

```
corta-fecha/
├── frontend/        Aplicacion SvelteKit
├── backend/         API FastAPI
│   └── db/schema.sql  Esquema PostgreSQL de referencia
├── docs/            Arquitectura, modelo de datos, reglas de negocio
├── docker-compose.yml
└── .env.example
```

## Arranque rapido (local, con Docker)

```bash
cp .env.example .env
docker compose up --build
```

- API:     http://localhost:8000  (docs: http://localhost:8000/docs)
- Frontend: http://localhost:5173
- Postgres: localhost:5432

## Arranque manual (sin Docker)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Base de datos

Cargar el esquema de referencia:

```bash
createdb corta_fecha
psql -d corta_fecha -f backend/db/schema.sql
```

Para cambios versionados usar Alembic (ver `backend/migrations/`).

## Modulos (MVP)

1. Inicio de sesion y roles basicos
2. Importacion / sincronizacion de inventario
3. Productos, lotes, vencimientos y cantidades
4. Inspeccion fisica con responsable y observaciones
5. Dashboard con clasificacion de vencimientos
6. Alertas automaticas
7. Exportacion a Excel
8. Historial de inspecciones y cambios
