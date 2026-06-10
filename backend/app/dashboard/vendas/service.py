from __future__ import annotations

from app.dashboard.vendas.queries import VENDAS_MOCK


class VendasService:
    def resumo(self, claims: dict) -> dict:
        return {
            "module": "vendas",
            "titulo": "Vendas",
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
            **VENDAS_MOCK["resumo"],
        }

    def top_produtos(self, claims: dict) -> dict:
        return {
            "module": "vendas",
            "titulo": "Top Produtos",
            "items": VENDAS_MOCK["top_produtos"],
        }

    def por_vendedor(self, claims: dict) -> dict:
        return {
            "module": "vendas",
            "titulo": "Por Vendedor",
            "items": VENDAS_MOCK["por_vendedor"],
        }


vendas_service = VendasService()
