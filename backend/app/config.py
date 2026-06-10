from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Dashboard Web Multiempresa API"
    secret_key: str = "change-this-secret"
    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 240
    company_token_expire_minutes: int = 30
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    bases_config_path: str = "data/bases_config.json"
    permissions_config_path: str = "data/permissions_config.json"
    firebird_driver: str = "fdb"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
