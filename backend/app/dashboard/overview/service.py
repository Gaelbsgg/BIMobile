from __future__ import annotations

from app.dashboard.overview.queries import OVERVIEW_MOCK


class OverviewService:
    def resumo(self, claims: dict) -> dict:
        return OVERVIEW_MOCK


overview_service = OverviewService()
