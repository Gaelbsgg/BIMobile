from __future__ import annotations

from app.dashboard.configuracoes.queries import CONFIGURACOES_MOCK


class ConfiguracoesService:
    def resumo(self, claims: dict) -> dict:
        return {
            **CONFIGURACOES_MOCK,
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
        }


configuracoes_service = ConfiguracoesService()
