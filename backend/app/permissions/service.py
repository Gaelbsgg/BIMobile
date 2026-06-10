from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import Depends, HTTPException, status

from app.config import get_settings
from app.core.jwt import get_current_claims
from app.core.exceptions import forbidden, not_found


def _hash_password(raw_password: str) -> str:
    return sha256(raw_password.encode("utf-8")).hexdigest()


class PermissionsService:
    def __init__(self, path: str):
        self.path = Path(path)
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(self._default_data())

    def _default_data(self) -> dict[str, Any]:
        demo_permissions = {
            "bases": {
                "base-demo-matriz": {
                    "users": [
                        {
                            "login": "ADMIN",
                            "nome": "Administrador",
                            "senha_hash": _hash_password("admin123"),
                            "roles": ["admin"],
                            "modules": ["overview", "vendas", "financeiro", "estoque", "funcionarios", "configuracoes"],
                            "kpis": ["vendas", "ticket_medio", "estoque", "pagar", "receber"],
                        },
                        {
                            "login": "VENDAS",
                            "nome": "Gestor de Vendas",
                            "senha_hash": _hash_password("vendas123"),
                            "roles": ["user"],
                            "modules": ["overview", "vendas"],
                            "kpis": ["vendas", "ticket_medio"],
                        },
                        {
                            "login": "GERENTE",
                            "nome": "Gestor Admin",
                            "senha_hash": _hash_password("123456"),
                            "roles": ["admin"],
                            "modules": ["overview", "vendas", "financeiro", "estoque", "funcionarios", "configuracoes"],
                            "kpis": ["vendas", "ticket_medio", "estoque", "pagar", "receber"],
                        },
                        {
                            "login": "VENDEDOR",
                            "nome": "Vendedor Comercial",
                            "senha_hash": _hash_password("vendas123"),
                            "roles": ["user"],
                            "modules": ["overview", "vendas"],
                            "kpis": ["vendas", "ticket_medio"],
                        },
                    ]
                },
                "base-demo-filial": {
                    "users": [
                        {
                            "login": "SUPERVISOR",
                            "nome": "Supervisor Filial",
                            "senha_hash": _hash_password("123456"),
                            "roles": ["user"],
                            "modules": ["overview", "estoque", "funcionarios"],
                            "kpis": ["estoque", "funcionarios"],
                        }
                    ]
                },
            }
        }
        return demo_permissions

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

    def list_permissions(self, base_id: str) -> list[dict[str, Any]]:
        base_permissions = self.read().get("bases", {}).get(base_id, {})
        return base_permissions.get("users", [])

    def get_permission(self, base_id: str, login: str) -> dict[str, Any] | None:
        login_normalized = login.strip().upper()
        return next((item for item in self.list_permissions(base_id) if item.get("login", "").upper() == login_normalized), None)

    def public_permission(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "login": item.get("login"),
            "nome": item.get("nome"),
            "roles": item.get("roles", []),
            "modules": item.get("modules", []),
            "kpis": item.get("kpis", []),
        }

    def upsert_permission(self, base_id: str, login: str, payload: dict[str, Any]) -> dict[str, Any]:
        login_normalized = login.strip().upper()

        def updater(data):
            bases = data.setdefault("bases", {})
            base_permissions = bases.setdefault(base_id, {"users": []})
            users = base_permissions.setdefault("users", [])
            item = next((user for user in users if user.get("login", "").upper() == login_normalized), None)
            if item is None:
                item = {"login": login_normalized}
                users.append(item)
            item.update(
                {
                    "login": login_normalized,
                    "nome": payload.get("nome") or item.get("nome") or login_normalized.title(),
                    "roles": payload.get("roles", item.get("roles", [])),
                    "modules": payload.get("modules", item.get("modules", [])),
                    "kpis": payload.get("kpis", item.get("kpis", [])),
                }
            )
            if payload.get("senha"):
                item["senha_hash"] = _hash_password(payload["senha"])
            return data

        updated = self.update(updater)
        return self.public_permission(self.get_permission(base_id, login_normalized) or {})

    def validate_local_login(self, base_id: str, login: str, senha: str) -> dict[str, Any] | None:
        permission = self.get_permission(base_id, login)
        if permission and permission.get("senha_hash") == _hash_password(senha):
            return permission
        return None

    def ensure_module_access(self, claims: dict[str, Any], module: str) -> None:
        permissions = claims.get("permissions", {})
        allowed_modules = permissions.get("modules", [])
        if module not in allowed_modules and "admin" not in claims.get("roles", []):
            raise forbidden("Sem permissão para este módulo")

    def dependency_for_module(self, module: str):
        def dependency(claims: dict[str, Any] = Depends(get_current_claims)) -> dict[str, Any]:
            self.ensure_module_access(claims, module)
            return claims

        return dependency

    def public_permissions_for_base(self, base_id: str) -> list[dict[str, Any]]:
        return [self.public_permission(item) for item in self.list_permissions(base_id)]


def get_permissions_service() -> PermissionsService:
    settings = get_settings()
    return PermissionsService(settings.resolve_path(settings.permissions_config_path))
