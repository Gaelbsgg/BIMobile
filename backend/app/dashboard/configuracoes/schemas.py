from __future__ import annotations

from pydantic import BaseModel, Field


class ConfiguracoesItemResponse(BaseModel):
    chave: str
    valor: str


class ConfiguracoesResumoResponse(BaseModel):
    module: str
    titulo: str
    items: list[ConfiguracoesItemResponse] = Field(default_factory=list)
