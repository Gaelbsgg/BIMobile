from __future__ import annotations

from typing import Any

from app.database.base_registry import BaseRegistry, get_base_registry
from app.database.firebird import test_connection


class ConnectionManager:
    def __init__(self, registry: BaseRegistry | None = None):
        self.registry = registry or get_base_registry()

    def list_bases(self) -> list[dict[str, Any]]:
        return self.registry.list_bases()

    def get_base(self, base_id: str) -> dict[str, Any] | None:
        return self.registry.get_by_id(base_id)

    def get_bases_by_token(self, token: str) -> list[dict[str, Any]]:
        return [base for base in self.registry.get_by_token(token) if base.get("ativo", True)]

    def get_primary_base_by_token(self, token: str, base_id: str | None = None) -> dict[str, Any]:
        bases = self.get_bases_by_token(token)
        if base_id:
            selected = next((base for base in bases if base.get("id") == base_id), None)
            if selected is None:
                raise KeyError(base_id)
            return selected
        if not bases:
            raise KeyError(token)
        return bases[0]

    def company_metadata(self, base_config: dict[str, Any]) -> dict[str, Any]:
        return {
            "nome": base_config.get("empresa_nome") or base_config.get("nome_configuracao") or "Empresa Demo",
            "cnpj": base_config.get("empresa_cnpj") or "00.000.000/0001-00",
        }

    def test_base_connection(self, base_config: dict[str, Any]) -> dict[str, Any]:
        return test_connection(base_config)


def get_connection_manager() -> ConnectionManager:
    return ConnectionManager()
