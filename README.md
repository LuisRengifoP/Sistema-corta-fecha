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

Migraciones SQL ya incluidas (aplicar en orden sobre una base existente):

```bash
psql "$DATABASE_URL" -f backend/migrations/001_inventario_cajas_unidades.sql
```

- `001_inventario_cajas_unidades.sql`: agrega `inventario_lotes.cajas` y
  `inventario_lotes.unidades_sueltas` para guardar el desglose que declara el
  encargado en vez de derivarlo del factor de empaque.

## PWA (instalable y uso sin conexion)

El frontend es una PWA: se instala en movil y escritorio (WebAPK en Android)
y usa un Service Worker generado con Workbox a traves de `vite-plugin-pwa` y
`@vite-pwa/sveltekit` (configuracion en `frontend/vite.config.ts`).

Que cachea:

- El shell de la app y los assets del build (precache de Workbox).
- Las pantallas visitadas: `NetworkFirst`, con la copia local como respaldo.
- Las lecturas GET de la API: `NetworkFirst` con copia valida 24 h, para
  consultar los ultimos datos sin conexion. Esa cache se borra al cerrar
  sesion, para que un usuario no vea datos del anterior en el mismo equipo.
- Las fuentes de Google: `CacheFirst` por un ano.
- Sin conexion y sin copia local se muestra `frontend/static/offline.html`.

Probar la PWA (el Service Worker esta desactivado en `npm run dev`):

```bash
cd frontend
npm run build
node build
```

Luego abrir la app en `http://localhost:3000` e instalarla desde el aviso de
la propia app o desde el menu del navegador. Fuera de `localhost` el
navegador solo ofrece la instalacion si el sitio se sirve por HTTPS.

Iconos y manifiesto: `frontend/static/icons/` y la clave `manifest` de
`frontend/vite.config.ts`.

## Modulos (MVP)

1. Inicio de sesion y roles basicos
2. Importacion / sincronizacion de inventario
3. Productos, lotes, vencimientos y cantidades
4. Inspeccion fisica con responsable y observaciones
5. Dashboard con clasificacion de vencimientos
6. Alertas automaticas
7. Exportacion a Excel
8. Historial de inspecciones y cambios
