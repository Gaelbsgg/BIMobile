from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.runtime_config import load_runtime_config, resolve_runtime_path, runtime_config_path


RUNTIME_CONFIG = load_runtime_config()


class Settings(BaseSettings):
    app_name: str = str(RUNTIME_CONFIG["app"]["name"])
    app_company: str = str(RUNTIME_CONFIG["app"]["company"])
    app_version: str = str(RUNTIME_CONFIG["app"]["version"])
    secret_key: str = "change-this-secret"
    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 240
    company_token_expire_minutes: int = 30
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    api_host: str = str(RUNTIME_CONFIG["api"]["host"])
    api_port: int = int(RUNTIME_CONFIG["api"]["port"])
    api_exe: str = str(RUNTIME_CONFIG["api"]["exe"])
    docs_url: str = str(RUNTIME_CONFIG["api"]["docs_url"])
    health_url: str = str(RUNTIME_CONFIG["api"]["health_url"])
    service_name: str = str(RUNTIME_CONFIG["service"]["name"])
    service_display_name: str = str(RUNTIME_CONFIG["service"]["display_name"])
    service_description: str = str(RUNTIME_CONFIG["service"]["description"])
    data_path: str = str(RUNTIME_CONFIG["paths"]["data"])
    logs_path: str = str(RUNTIME_CONFIG["paths"]["logs"])
    bases_config_path: str = str(RUNTIME_CONFIG["paths"]["bases_config"])
    permissions_config_path: str = str(RUNTIME_CONFIG["paths"]["permissions_config"])
    store_path: str = str(resolve_runtime_path("../data/local_store.json"))
    firebird_driver: str = "fdb"
    cloudflared_enabled: bool = bool(RUNTIME_CONFIG["cloudflared"]["enabled"])
    cloudflared_exe: str = str(RUNTIME_CONFIG["cloudflared"]["exe"])
    cloudflared_tunnel_url: str = str(RUNTIME_CONFIG["cloudflared"]["tunnel_url"])
    runtime_config_path: str = str(runtime_config_path())

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def signing_secret(self) -> str:
        return self.secret_key or self.jwt_secret

    def resolve_path(self, relative_path: str) -> str:
        return str(resolve_runtime_path(relative_path))


@lru_cache
def get_settings() -> Settings:
    return Settings()
