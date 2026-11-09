from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion de la aplicacion, cargada desde variables de entorno / .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Base de datos
    DATABASE_URL: str = "postgresql+psycopg://corta_fecha:cambia_esta_clave@localhost:5432/corta_fecha"

    # Seguridad / JWT
    JWT_SECRET: str = "cambia_este_secreto"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS (lista separada por comas)
    CORS_ORIGINS: str = "http://localhost:5173"

    # Almacenamiento de evidencias
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_PATH: str = "./storage"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
