from __future__ import annotations

from pydantic import BaseModel, Field


class VendasResumoResponse(BaseModel):
    faturamento: float
    ticket_medio: float
    quantidade: int


class VendasItemResponse(BaseModel):
    produto: str | None = None
    vendedor: str | None = None
    quantidade: int | None = None
    vendas: int | None = None
    valor: float


class VendasListResponse(BaseModel):
    items: list[VendasItemResponse] = Field(default_factory=list)

