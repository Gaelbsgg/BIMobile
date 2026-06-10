OVERVIEW_RESUMO_SQL = """
SELECT
    1284500.00 AS total_geral_vendas,
    450.22 AS ticket_medio,
    2854 AS quantidade_vendas,
    342120.50 AS total_receber,
    185400.00 AS total_pagar,
    954200.00 AS recebido_periodo,
    720000.00 AS pago_periodo,
    4520000.00 AS valor_estoque,
    42 AS produtos_abaixo_minimo
FROM RDB$DATABASE
"""

OVERVIEW_MOCK = {
    "total_geral_vendas": 1284500.00,
    "ticket_medio": 450.22,
    "quantidade_vendas": 2854,
    "total_receber": 342120.50,
    "total_pagar": 185400.00,
    "recebido_periodo": 954200.00,
    "pago_periodo": 720000.00,
    "valor_estoque": 4520000.00,
    "produtos_abaixo_minimo": 42,
}
