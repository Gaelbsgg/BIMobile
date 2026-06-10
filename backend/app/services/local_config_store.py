from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.core.config import get_settings
from app.core.passwords import hash_password


class LocalConfigStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(self._default_data())

    def _default_data(self) -> dict[str, Any]:
        return {
            "companies": [
                {
                    "id": "demo-company",
                    "token": "EMP-001",
                    "name": "Empresa Demo",
                    "status": "active",
                    "bases": [
                        {
                            "id": "base-1",
                            "name": "Matriz",
                            "alias": "matriz",
                            "path": "C:/dados/matriz.fdb",
                            "host": "127.0.0.1",
                            "port": 3050,
                            "username": "sysdba",
                            "charset": "UTF8",
                            "status": "mock",
                        }
                    ],
                    "users": [
                        {
                            "id": "user-admin",
                            "name": "Administrador",
                            "username": "admin",
                            "password_hash": hash_password("admin123"),
                            "roles": ["admin"],
                            "permissions": {
                                "modules": [
                                    "overview",
                                    "vendas",
                                    "financeiro",
                                    "estoque",
                                    "funcionarios",
                                    "configuracoes",
                                ],
                                "kpis": [
                                    "vendas",
                                    "pedidos",
                                    "margem",
                                    "tickets",
                                    "estoque",
                                    "funcionarios",
                                ],
                            },
                        },
                        {
                            "id": "user-gestor-vendas",
                            "name": "Gestor de Vendas",
                            "username": "vendas",
                            "password_hash": hash_password("vendas123"),
                            "roles": ["user"],
                            "permissions": {
                                "modules": ["overview", "vendas"],
                                "kpis": ["vendas", "tickets"],
                            },
                        },
                    ],
                }
            ],
            "sql_registry": [
                {
                    "id": "overview-kpis",
                    "module": "overview",
                    "description": "KPIs consolidados do dashboard",
                    "dialect": "firebird-2.5",
                    "status": "mock",
                },
                {
                    "id": "sales-by-period",
                    "module": "vendas",
                    "description": "Vendas por período",
                    "dialect": "firebird-2.5",
                    "status": "mock",
                },
            ],
        }

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def read(self) -> dict[str, Any]:
        with self._lock:
            return self._read()

    def write(self, data: dict[str, Any]) -> None:
        with self._lock:
            self._write(data)

    def update(self, updater) -> dict[str, Any]:
        with self._lock:
            data = self._read()
            updated = updater(data)
            self._write(updated)
            return updated


def get_store() -> LocalConfigStore:
    settings = get_settings()
    return LocalConfigStore(settings.store_path)
