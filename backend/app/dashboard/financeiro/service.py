from __future__ import annotations

from app.dashboard.financeiro.queries import FINANCEIRO_MOCK


class FinanceiroService:
    def resumo(self, claims: dict) -> dict:
        return {
            "module": "financeiro",
            "titulo": "Financeiro",
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
            **FINANCEIRO_MOCK["resumo"],
        }

    def contas_receber(self, claims: dict) -> dict:
        return {
            "module": "financeiro",
            "titulo": "Contas a Receber",
            "items": FINANCEIRO_MOCK["contas_receber"],
        }

    def contas_pagar(self, claims: dict) -> dict:
        return {
            "module": "financeiro",
            "titulo": "Contas a Pagar",
            "items": FINANCEIRO_MOCK["contas_pagar"],
        }


financeiro_service = FinanceiroService()
