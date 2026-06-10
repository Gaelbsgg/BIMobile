from __future__ import annotations

from app.services.local_config_store import get_store


class SQLRegistryService:
    def list_queries(self) -> list[dict]:
        return get_store().read().get("sql_registry", [])

    def get_query(self, query_id: str) -> dict | None:
        for query in self.list_queries():
            if query["id"] == query_id:
                return query
        return None


sql_registry_service = SQLRegistryService()
