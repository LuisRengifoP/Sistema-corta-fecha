import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, health
from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("corta_fecha")

app = FastAPI(
    title="Sistema Corta Fecha API",
    version="0.1.0",
    description="API para control de productos proximos a vencer y averiados.",
)


# Este middleware se registra ANTES del de CORS para que quede por dentro:
# asi cualquier error no previsto se convierte en una respuesta JSON 500 que
# todavia pasa por CORSMiddleware y recibe las cabeceras Access-Control-*.
# Sin esto el navegador no ve la respuesta y solo informa "Failed to fetch".
@app.middleware("http")
async def errores_con_cors(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception:  # noqa: BLE001
        logger.exception("Error no controlado en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor"},
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(api_router)


@app.get("/")
def root() -> dict:
    return {"service": "corta-fecha", "docs": "/docs"}
