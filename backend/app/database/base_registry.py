from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from app.config import get_settings


class BaseRegistry:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(self._default_data())

    def _default_data(self) -> dict[str, Any]:
        return {
            "bases": [
                {
                    "id": "base-demo-matriz",
                    "nome_configuracao": "Matriz",
                    "token_empresa": "001",
                    "servidor": "127.0.0.1",
                    "porta": 3050,
                    "caminho_fdb": "C:/firebird/dados/matriz.fdb",
                    "usuario_firebird": "SYSDBA",
                    "senha_firebird": "masterkey",
                    "ativo": True,
                    "empresa_nome": "Empresa Demo Matriz",
                    "empresa_cnpj": "00.000.000/0001-00",
                },
                {
                    "id": "base-demo-filial",
                    "nome_configuracao": "Filial",
                    "token_empresa": "001",
                    "servidor": "127.0.0.1",
                    "porta": 3050,
                    "caminho_fdb": "C:/firebird/dados/filial.fdb",
                    "usuario_firebird": "SYSDBA",
                    "senha_firebird": "masterkey",
                    "ativo": True,
                    "empresa_nome": "Empresa Demo Matriz",
                    "empresa_cnpj": "00.000.000/0001-00",
                },
            ]
        }

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

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

    def list_bases(self) -> list[dict[str, Any]]:
        return self.read().get("bases", [])

    def get_by_id(self, base_id: str) -> dict[str, Any] | None:
        return next((base for base in self.list_bases() if base.get("id") == base_id), None)

    def get_by_token(self, token: str) -> list[dict[str, Any]]:
        return [base for base in self.list_bases() if str(base.get("token_empresa")) == str(token)]

    def public_base(self, base: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": base.get("id"),
            "nome_configuracao": base.get("nome_configuracao"),
            "token_empresa": base.get("token_empresa"),
            "servidor": base.get("servidor"),
            "porta": base.get("porta"),
            "ativo": base.get("ativo", True),
            "empresa_nome": base.get("empresa_nome"),
            "empresa_cnpj": base.get("empresa_cnpj"),
        }

    def create_base(self, payload: dict[str, Any]) -> dict[str, Any]:
        def updater(data):
            bases = data.setdefault("bases", [])
            new_base = {
                "id": payload.get("id") or f"base-{len(bases) + 1}",
                "nome_configuracao": payload.get("nome_configuracao", "Nova Base"),
                "token_empresa": payload.get("token_empresa", ""),
                "servidor": payload.get("servidor", "127.0.0.1"),
                "porta": payload.get("porta", 3050),
                "caminho_fdb": payload.get("caminho_fdb", ""),
                "usuario_firebird": payload.get("usuario_firebird", "SYSDBA"),
                "senha_firebird": payload.get("senha_firebird", "masterkey"),
                "ativo": payload.get("ativo", True),
                "empresa_nome": payload.get("empresa_nome", payload.get("nome_configuracao", "Empresa")),
                "empresa_cnpj": payload.get("empresa_cnpj", "00.000.000/0001-00"),
            }
            bases.append(new_base)
            return data

        updated = self.update(updater)
        return updated["bases"][-1]

    def update_base(self, base_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        def updater(data):
            base = next((item for item in data.get("bases", []) if item.get("id") == base_id), None)
            if base is None:
                raise KeyError(base_id)
            base.update(payload)
            return data

        updated = self.update(updater)
        return next(base for base in updated.get("bases", []) if base.get("id") == base_id)

    def delete_base(self, base_id: str) -> None:
        def updater(data):
            data["bases"] = [base for base in data.get("bases", []) if base.get("id") != base_id]
            return data

        self.update(updater)


def get_base_registry() -> BaseRegistry:
    settings = get_settings()
    return BaseRegistry(settings.bases_config_path)
