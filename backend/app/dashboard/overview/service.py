from __future__ import annotations

from app.dashboard.overview.queries import OVERVIEW_MOCK


class OverviewService:
    def resumo(self, claims: dict) -> dict:
        return {
            "module": "overview",
            "titulo": "Visão Geral",
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
            **OVERVIEW_MOCK,
        }


overview_service = OverviewService()
