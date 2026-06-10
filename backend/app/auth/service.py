from __future__ import annotations

from fastapi import HTTPException, status

from app.config import get_settings
from app.core.jwt import create_access_token, decode_access_token
from app.core.exceptions import unauthorized
from app.database.connection_manager import get_connection_manager
from app.permissions.service import get_permissions_service


class AuthService:
    def __init__(self):
        self.connection_manager = get_connection_manager()
        self.permissions_service = get_permissions_service()

    def resolve_company(self, token: str, base_id: str | None = None) -> dict:
        bases = self.connection_manager.get_bases_by_token(token)
        if not bases:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token da empresa inválido")
        try:
            selected = self.connection_manager.get_primary_base_by_token(token, base_id)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base da empresa não encontrada") from exc
        metadata = self.connection_manager.company_metadata(selected)
        return {
            "id": f"company-{token}",
            "name": metadata["nome"],
            "token": token,
            "cnpj": metadata["cnpj"],
            "base_id": selected["id"],
            "bases": [
                {
                    "id": base.get("id"),
                    "name": base.get("nome_configuracao"),
                    "alias": base.get("nome_configuracao", "").lower().replace(" ", "-"),
                    "host": base.get("servidor"),
                    "port": base.get("porta"),
                    "charset": "UTF8",
                    "status": "mock" if base.get("ativo", True) else "inactive",
                }
                for base in bases
            ],
        }

    def create_company_challenge(self, token: str) -> dict:
        company = self.resolve_company(token)
        settings = get_settings()
        empresa_token = create_access_token(
            {
                "type": "company_challenge",
                "company_token": token,
                "base_id": company["base_id"],
            },
            settings.company_token_expire_minutes,
        )
        return {
            "empresa_token": empresa_token,
            "company": company,
        }

    def login(self, payload: dict) -> dict:
        token = payload["token"]
        login = payload["login"]
        senha = payload["senha"]
        base_id = payload.get("base_id")

        company_token = token
        if token.count(".") == 2:
            challenge = decode_access_token(token)
            if challenge.get("type") == "company_challenge":
                company_token = challenge.get("company_token", token)
                base_id = base_id or challenge.get("base_id")

        try:
            selected_base = self.connection_manager.get_primary_base_by_token(company_token, base_id)
        except KeyError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base da empresa não encontrada") from exc
        company = self.resolve_company(company_token, selected_base["id"])
        permission = self.permissions_service.validate_local_login(selected_base["id"], login, senha)
        if permission is None:
            raise unauthorized("Credenciais inválidas")

        settings = get_settings()
        user_permissions = {
            "modules": permission.get("modules", []),
            "kpis": permission.get("kpis", []),
        }
        access_token = create_access_token(
            {
                "type": "access",
                "company_token": company_token,
                "base_id": selected_base["id"],
                "login": permission.get("login", login).upper(),
                "name": permission.get("nome") or permission.get("login", login),
                "roles": permission.get("roles", []),
                "permissions": user_permissions,
            },
            settings.access_token_expire_minutes,
        )
        user_id = f"{selected_base['id']}:{permission.get('login', login).upper()}"
        user_payload = {
            "id": user_id,
            "login": permission.get("login", login).upper(),
            "nome": permission.get("nome") or permission.get("login", login),
            "name": permission.get("nome") or permission.get("login", login),
            "username": permission.get("login", login).upper(),
            "roles": permission.get("roles", []),
            "permissions": user_permissions,
            "base_id": selected_base["id"],
        }
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_payload,
            "company": company,
            "permissions": user_permissions,
        }

    def me_from_claims(self, claims: dict) -> dict:
        if claims.get("type") != "access":
            raise unauthorized("Token inválido")
        company = self.resolve_company(claims.get("company_token", ""), claims.get("base_id"))
        return {
            "user": {
                "id": f"{claims.get('base_id')}:{claims.get('login')}",
                "login": claims.get("login"),
                "nome": claims.get("name"),
                "name": claims.get("name"),
                "username": claims.get("login"),
                "roles": claims.get("roles", []),
                "permissions": claims.get("permissions", {}),
                "base_id": claims.get("base_id"),
            },
            "company": company,
            "permissions": claims.get("permissions", {}),
        }


auth_service = AuthService()
