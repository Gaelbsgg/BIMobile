from __future__ import annotations

import json
import os
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
                self._normalize_base(
                    {
                        "id": "base-demo-matriz",
                        "apelido": "Matriz",
                        "descricao": "Matriz",
                        "servidor": "127.0.0.1",
                        "porta": 3050,
                        "caminho_base": "C:/firebird/dados/",
                        "nome_arquivo": "matriz.fdb",
                        "caminho_fdb": "C:/firebird/dados/matriz.fdb",
                        "usuario_firebird": "SYSDBA",
                        "senha_firebird": "masterkey",
                        "protocolo": "TCP-IP",
                        "servidor_linux": False,
                        "ativo": True,
                        "base_padrao": True,
                        "token_empresa": "001",
                        "empresa_nome": "Empresa Demo Matriz",
                        "empresa_cnpj": "00.000.000/0001-00",
                    }
                ),
                self._normalize_base(
                    {
                        "id": "base-demo-filial",
                        "apelido": "Filial",
                        "descricao": "Filial",
                        "servidor": "127.0.0.1",
                        "porta": 3050,
                        "caminho_base": "C:/firebird/dados/",
                        "nome_arquivo": "filial.fdb",
                        "caminho_fdb": "C:/firebird/dados/filial.fdb",
                        "usuario_firebird": "SYSDBA",
                        "senha_firebird": "masterkey",
                        "protocolo": "TCP-IP",
                        "servidor_linux": False,
                        "ativo": True,
                        "base_padrao": False,
                        "token_empresa": "001",
                        "empresa_nome": "Empresa Demo Matriz",
                        "empresa_cnpj": "00.000.000/0001-00",
                    }
                ),
            ]
        }

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write(self, data: dict[str, Any]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def _normalize_base(self, base: dict[str, Any]) -> dict[str, Any]:
        descricao = base.get("descricao") or base.get("nome_configuracao") or base.get("apelido") or "Nova Base"
        apelido = base.get("apelido") or descricao
        caminho_fdb = base.get("caminho_fdb") or ""
        caminho_base = base.get("caminho_base") or ""
        nome_arquivo = base.get("nome_arquivo") or ""

        if caminho_fdb and not caminho_base:
            caminho_base = str(Path(caminho_fdb).parent) + os.sep
        if caminho_fdb and not nome_arquivo:
            nome_arquivo = Path(caminho_fdb).name
        if not caminho_fdb and caminho_base and nome_arquivo:
            caminho_fdb = str(Path(caminho_base) / nome_arquivo)

        return {
            "id": base.get("id") or "base-001",
            "apelido": apelido,
            "descricao": descricao,
            "nome_configuracao": base.get("nome_configuracao") or descricao,
            "token_empresa": base.get("token_empresa", ""),
            "servidor": base.get("servidor") or base.get("host") or "127.0.0.1",
            "porta": int(base.get("porta") or base.get("port") or 3050),
            "caminho_base": caminho_base,
            "nome_arquivo": nome_arquivo,
            "caminho_fdb": caminho_fdb,
            "usuario_firebird": base.get("usuario_firebird") or base.get("username") or "SYSDBA",
            "senha_firebird": base.get("senha_firebird") or base.get("password") or "masterkey",
            "protocolo": base.get("protocolo") or "TCP-IP",
            "servidor_linux": bool(base.get("servidor_linux", False)),
            "ativo": bool(base.get("ativo", True)),
            "base_padrao": bool(base.get("base_padrao", False)),
            "empresa_nome": base.get("empresa_nome") or base.get("empresa") or descricao,
            "empresa_cnpj": base.get("empresa_cnpj") or base.get("cnpj"),
        }

    def _normalize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        bases = [self._normalize_base(base) for base in data.get("bases", [])]
        selecionada = bool(data.get("selecionar_base_ao_iniciar", False))
        return {
            "bases": bases,
            "selecionar_base_ao_iniciar": selecionada,
        }

    def read(self) -> dict[str, Any]:
        with self._lock:
            return self._normalize_data(self._read())

    def write(self, data: dict[str, Any]) -> None:
        with self._lock:
            self._write(self._normalize_data(data))

    def update(self, updater) -> dict[str, Any]:
        with self._lock:
            data = self._normalize_data(self._read())
            updated = updater(data)
            normalized = self._normalize_data(updated)
            self._write(normalized)
            return normalized

    def list_bases(self) -> list[dict[str, Any]]:
        return self.read().get("bases", [])

    def get_by_id(self, base_id: str) -> dict[str, Any] | None:
        return next((base for base in self.list_bases() if base.get("id") == base_id), None)

    def get_by_token(self, token: str) -> list[dict[str, Any]]:
        return [base for base in self.list_bases() if str(base.get("token_empresa")) == str(token)]

    def public_base(self, base: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_base(base)
        return {
            "id": normalized.get("id"),
            "apelido": normalized.get("apelido"),
            "descricao": normalized.get("descricao"),
            "nome_configuracao": normalized.get("nome_configuracao"),
            "token_empresa": normalized.get("token_empresa"),
            "servidor": normalized.get("servidor"),
            "porta": normalized.get("porta"),
            "caminho_base": normalized.get("caminho_base"),
            "nome_arquivo": normalized.get("nome_arquivo"),
            "caminho_fdb": normalized.get("caminho_fdb"),
            "usuario_firebird": normalized.get("usuario_firebird"),
            "senha_firebird": normalized.get("senha_firebird"),
            "protocolo": normalized.get("protocolo"),
            "servidor_linux": normalized.get("servidor_linux"),
            "ativo": normalized.get("ativo", True),
            "base_padrao": normalized.get("base_padrao", False),
            "empresa_nome": normalized.get("empresa_nome"),
            "empresa_cnpj": normalized.get("empresa_cnpj"),
        }

    def create_base(self, payload: dict[str, Any]) -> dict[str, Any]:
        def updater(data):
            bases = data.setdefault("bases", [])
            new_id = payload.get("id") or f"base-{len(bases) + 1:03d}"
            new_base = self._normalize_base({**payload, "id": new_id})
            if new_base.get("base_padrao"):
                for base in bases:
                    base["base_padrao"] = False
            bases.append(new_base)
            return data

        updated = self.update(updater)
        return updated["bases"][-1]

    def update_base(self, base_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        def updater(data):
            base = next((item for item in data.get("bases", []) if item.get("id") == base_id), None)
            if base is None:
                raise KeyError(base_id)
            merged = self._normalize_base({**base, **payload, "id": base_id})
            if merged.get("base_padrao"):
                for item in data.get("bases", []):
                    item["base_padrao"] = item.get("id") == base_id
            base.clear()
            base.update(merged)
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
    return BaseRegistry(settings.resolve_path(settings.bases_config_path))
