from __future__ import annotations

from pydantic import BaseModel, Field


class EstoqueResumoResponse(BaseModel):
    valor_estoque: float
    produtos_abaixo_minimo: int
    skus: int


class EstoqueItemResponse(BaseModel):
    produto: str
    saldo: float
    minimo: float


class EstoqueListResponse(BaseModel):
    items: list[EstoqueItemResponse] = Field(default_factory=list)

