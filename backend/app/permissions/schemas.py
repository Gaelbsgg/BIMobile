from __future__ import annotations

from pydantic import BaseModel, Field


class PermissionUpsertPayload(BaseModel):
    nome: str | None = None
    login: str | None = None
    senha: str | None = None
    roles: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)


class PermissionsItem(BaseModel):
    login: str
    nome: str | None = None
    roles: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)


class PermissionsListResponse(BaseModel):
    base_id: str
    items: list[PermissionsItem]
