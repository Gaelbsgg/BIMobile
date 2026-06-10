from __future__ import annotations

from pydantic import BaseModel, Field


class BasePayload(BaseModel):
    nome_configuracao: str = Field(min_length=1)
    token_empresa: str = Field(min_length=1)
    servidor: str = Field(default="127.0.0.1")
    porta: int = Field(default=3050, ge=1, le=65535)
    caminho_fdb: str = Field(min_length=1)
    usuario_firebird: str = Field(default="SYSDBA")
    senha_firebird: str = Field(min_length=1)
    ativo: bool = True
    empresa_nome: str | None = None
    empresa_cnpj: str | None = None


class BaseResponse(BaseModel):
    id: str
    nome_configuracao: str
    token_empresa: str
    servidor: str
    porta: int
    caminho_fdb: str
    usuario_firebird: str
    senha_firebird: str
    ativo: bool
    empresa_nome: str | None = None
    empresa_cnpj: str | None = None


class PermissionPayload(BaseModel):
    nome: str | None = None
    login: str | None = None
    senha: str | None = None
    roles: list[str] = Field(default_factory=list)
    modules: list[str] = Field(default_factory=list)
    kpis: list[str] = Field(default_factory=list)
