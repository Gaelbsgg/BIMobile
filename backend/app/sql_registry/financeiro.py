FINANCEIRO_RESUMO_SQL = "SELECT 954200.00 AS recebido_periodo FROM RDB$DATABASE"
FINANCEIRO_CONTAS_RECEBER_SQL = "SELECT 342120.50 AS total_receber FROM RDB$DATABASE"
FINANCEIRO_CONTAS_PAGAR_SQL = "SELECT 185400.00 AS total_pagar FROM RDB$DATABASE"

FINANCEIRO_MOCK = {
    "resumo": {
        "recebido_periodo": 954200.0,
        "pago_periodo": 720000.0,
        "total_receber": 342120.5,
        "total_pagar": 185400.0,
    },
    "contas_receber": [
        {"descricao": "Cliente A", "valor": 42500.0, "vencimento": "2026-06-15"},
        {"descricao": "Cliente B", "valor": 18200.0, "vencimento": "2026-06-18"},
    ],
    "contas_pagar": [
        {"descricao": "Fornecedor A", "valor": 28500.0, "vencimento": "2026-06-12"},
        {"descricao": "Fornecedor B", "valor": 19400.0, "vencimento": "2026-06-20"},
    ],
}
