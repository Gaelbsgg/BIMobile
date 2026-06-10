from __future__ import annotations

from app.dashboard.estoque.queries import ESTOQUE_MOCK


class EstoqueService:
    def resumo(self, claims: dict) -> dict:
        return {
            "module": "estoque",
            "titulo": "Estoque",
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
            **ESTOQUE_MOCK["resumo"],
        }

    def baixo_minimo(self, claims: dict) -> dict:
        return {
            "module": "estoque",
            "titulo": "Baixo Mínimo",
            "items": ESTOQUE_MOCK["baixo_minimo"],
        }


estoque_service = EstoqueService()
