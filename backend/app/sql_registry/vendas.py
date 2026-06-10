VENDAS_RESUMO_SQL = "SELECT 124900.00 AS faturamento FROM RDB$DATABASE"
VENDAS_TOP_PRODUTOS_SQL = "SELECT 'Produto A' AS nome, 25 AS quantidade FROM RDB$DATABASE"
VENDAS_POR_VENDEDOR_SQL = "SELECT 'Ana' AS vendedor, 48 AS pedidos FROM RDB$DATABASE"

VENDAS_MOCK = {
    "resumo": {
        "faturamento": 124900.00,
        "ticket_medio": 450.22,
        "quantidade": 2854,
    },
    "top_produtos": [
        {"produto": "Produto A", "quantidade": 125, "valor": 24800.0},
        {"produto": "Produto B", "quantidade": 82, "valor": 16340.0},
        {"produto": "Produto C", "quantidade": 61, "valor": 12200.0},
    ],
    "por_vendedor": [
        {"vendedor": "Ana", "vendas": 48, "valor": 32000.0},
        {"vendedor": "Bruno", "vendas": 41, "valor": 27800.0},
        {"vendedor": "Carla", "vendas": 35, "valor": 22100.0},
    ],
}
