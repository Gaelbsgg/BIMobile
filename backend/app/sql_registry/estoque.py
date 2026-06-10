ESTOQUE_RESUMO_SQL = "SELECT 4520000.00 AS valor_estoque FROM RDB$DATABASE"
ESTOQUE_BAIXO_MINIMO_SQL = "SELECT 42 AS produtos_abaixo_minimo FROM RDB$DATABASE"

ESTOQUE_MOCK = {
    "resumo": {
        "valor_estoque": 4520000.0,
        "produtos_abaixo_minimo": 42,
        "skus": 3482,
    },
    "baixo_minimo": [
        {"produto": "Produto A", "saldo": 5, "minimo": 20},
        {"produto": "Produto B", "saldo": 2, "minimo": 15},
    ],
}
