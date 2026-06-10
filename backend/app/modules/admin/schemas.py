from pydantic import BaseModel, Field


class BasePayload(BaseModel):
    name: str
    alias: str | None = None
    path: str = Field(min_length=3)
    host: str = "127.0.0.1"
    port: int = 3050
    username: str = "sysdba"
    charset: str = "UTF8"
    status: str = "mock"


class PermissionPayload(BaseModel):
    modules: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
