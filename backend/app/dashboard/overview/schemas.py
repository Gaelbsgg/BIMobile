from __future__ import annotations

from pydantic import BaseModel


class OverviewResumoResponse(BaseModel):
    total_geral_vendas: float
    lucro_bruto: float
    ticket_medio: float
    previsto_receber_mes: float
    os_em_servico: int
    os_encerradas: int
    os_canceladas: int
    previsto_pagar_mes: float
    numero_vendas: int
    devolucoes: int
    qtd_produtos_vendidos: float
    orcamentos: int
    autorizacoes_nf: int
    valor_total_estoque: float
    custo_total_estoque: float
    quantidade_total_estoque: float
    estoque_abaixo_minimo: int
    estoque_acima_maximo: int
