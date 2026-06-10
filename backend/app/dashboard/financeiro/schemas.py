from __future__ import annotations

from pydantic import BaseModel, Field


class FinanceiroResumoResponse(BaseModel):
    recebido_periodo: float
    pago_periodo: float
    total_receber: float
    total_pagar: float


class FinanceiroItemResponse(BaseModel):
    descricao: str
    valor: float
    vencimento: str


class FinanceiroListResponse(BaseModel):
    items: list[FinanceiroItemResponse] = Field(default_factory=list)

