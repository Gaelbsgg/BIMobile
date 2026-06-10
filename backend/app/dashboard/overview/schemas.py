from __future__ import annotations

from pydantic import BaseModel


class OverviewResumoResponse(BaseModel):
    total_geral_vendas: float
    ticket_medio: float
    quantidade_vendas: int
    total_receber: float
    total_pagar: float
    recebido_periodo: float
    pago_periodo: float
    valor_estoque: float
    produtos_abaixo_minimo: int

