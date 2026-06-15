OVERVIEW_RESUMO_SQL = """
SELECT
    164383.55 AS total_geral_vendas,
    26762.39 AS lucro_bruto,
    649.74 AS ticket_medio,
    130594.30 AS previsto_receber_mes,
    48 AS os_em_servico,
    165 AS os_encerradas,
    5 AS os_canceladas,
    166403.12 AS previsto_pagar_mes,
    253 AS numero_vendas,
    0 AS devolucoes,
    776.2 AS qtd_produtos_vendidos,
    4 AS orcamentos,
    86 AS autorizacoes_nf,
    14964919.49 AS valor_total_estoque,
    2487675.32 AS custo_total_estoque,
    102984.34 AS quantidade_total_estoque,
    2002 AS estoque_abaixo_minimo,
    6438 AS estoque_acima_maximo
FROM RDB$DATABASE
"""

OVERVIEW_MOCK = {
    "total_geral_vendas": 164383.55,
    "lucro_bruto": 26762.39,
    "ticket_medio": 649.74,
    "previsto_receber_mes": 130594.30,
    "os_em_servico": 48,
    "os_encerradas": 165,
    "os_canceladas": 5,
    "previsto_pagar_mes": 166403.12,
    "numero_vendas": 253,
    "devolucoes": 0,
    "qtd_produtos_vendidos": 776.2,
    "orcamentos": 4,
    "autorizacoes_nf": 86,
    "valor_total_estoque": 14964919.49,
    "custo_total_estoque": 2487675.32,
    "quantidade_total_estoque": 102984.34,
    "estoque_abaixo_minimo": 2002,
    "estoque_acima_maximo": 6438,
}
