from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException, status

from app.auth.password_hash import password_match_method, verify_database_password
from app.auth.queries import SQL_EMPRESA_IDENTIDADE, SQL_USUARIO_POR_LOGIN
from app.config import get_settings
from app.core.exceptions import unauthorized
from app.core.jwt import create_access_token, decode_access_token
from app.database.connection_manager import get_connection_manager
from app.database.firebird import get_connection
from app.permissions.service import get_permissions_service


LOGGER = logging.getLogger(__name__)
PERMISSION_MODULES = ["overview", "vendas", "financeiro", "estoque", "funcionarios", "configuracoes"]


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

    def _decode_company_token(self, token: str, base_id: str | None) -> tuple[str, str | None]:
        company_token = token
        challenge_base_id = base_id
        if token.count(".") == 2:
            challenge = decode_access_token(token)
            if challenge.get("type") == "company_challenge":
                company_token = challenge.get("company_token", token)
                challenge_base_id = challenge_base_id or challenge.get("base_id")
        return company_token, challenge_base_id

    def _looks_like_jwt(self, value: str) -> bool:
        return value.count(".") == 2

    def _fetch_first_row(self, base_config: dict[str, Any], sql: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        connection = get_connection(base_config)
        try:
            cursor = connection.cursor()
            cursor.execute(sql, params or {})
            row = cursor.fetchone()
            if row is None:
                return None
            columns = [column[0].lower() for column in cursor.description or []]
            return dict(zip(columns, row))
        finally:
            if hasattr(connection, "close"):
                connection.close()

    def _build_permissions(self) -> dict[str, Any]:
        return {
            "modules": PERMISSION_MODULES,
            "kpis": [],
        }

    def _build_success_response(
        self,
        *,
        base_id: str,
        base_config: dict[str, Any] | None = None,
        company_name: str,
        company_cnpj: str,
        token_empresa: str,
        login: str,
        nome_usuario: str,
        user_roles: list[str] | None = None,
    ) -> dict:
        settings = get_settings()
        permissions = self._build_permissions()
        access_token = create_access_token(
            {
                "type": "access",
                "base_id": base_id,
                "login": login,
                "nome_usuario": nome_usuario,
                "nome_empresa": company_name,
                "cnpj": company_cnpj,
                "token_empresa": token_empresa,
                "company_token": token_empresa,
                "username": login,
                "name": nome_usuario,
                "roles": user_roles or ["user"],
                "permissions": permissions,
            },
            settings.access_token_expire_minutes,
        )
        usuario = {
            "login": login,
            "nome": nome_usuario,
        }
        empresa = {
            "base_id": base_id,
            "nome": company_name,
            "cnpj": company_cnpj,
            "token_empresa": token_empresa,
        }
        user_payload = {
            "id": f"{base_id}:{login}",
            "login": login,
            "nome": nome_usuario,
            "name": nome_usuario,
            "username": login,
            "roles": user_roles or ["user"],
            "permissions": permissions,
            "base_id": base_id,
        }
        company_payload = {
            "id": f"company-{token_empresa}",
            "name": company_name,
            "token": token_empresa,
            "cnpj": company_cnpj,
            "base_id": base_id,
            "bases": [
                {
                    "id": base_id,
                    "name": company_name,
                    "alias": company_name.lower().replace(" ", "-"),
                    "host": base_config.get("servidor") if base_config else None,
                    "port": base_config.get("porta") if base_config else None,
                    "charset": base_config.get("charset") if base_config else None,
                    "status": "active",
                }
            ],
        }
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": usuario,
            "empresa": empresa,
            "permissoes": {
                "visao_geral": True,
                "vendas": True,
                "financeiro": True,
                "estoque": True,
                "funcionarios": True,
                "configuracoes": True,
            },
            "user": user_payload,
            "company": company_payload,
            "permissions": permissions,
        }

    def _login_real_firebird(self, payload: dict[str, Any], company_token: str, base_id: str) -> dict:
        base_config = self.connection_manager.get_base(base_id)
        if base_config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base da empresa não encontrada")

        empresa_row = self._fetch_first_row(base_config, SQL_EMPRESA_IDENTIDADE)
        if empresa_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token da empresa inválido.")

        db_token_empresa = str(empresa_row.get("loginliberacao") or "").strip()
        if str(payload.get("token") or "").strip() != db_token_empresa:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token da empresa inválido.")

        empresa_token_payload = str(payload.get("empresa_token") or "").strip()
        if empresa_token_payload and not self._looks_like_jwt(empresa_token_payload) and empresa_token_payload != str(
            empresa_row.get("nomefantasia") or ""
        ).strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empresa informada não confere com a base selecionada.",
            )

        login = str(payload.get("login") or "").strip()
        if not login:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login ou senha inválidos.")

        usuario_row = self._fetch_first_row(base_config, SQL_USUARIO_POR_LOGIN, {"LOGIN": login})
        if usuario_row is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login ou senha inválidos.")

        if str(usuario_row.get("inativo") or "").strip().upper() == "T":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário está inativo.")

        senha_informada = str(payload.get("senha") or "")
        senha_hash = str(usuario_row.get("senha") or "")
        match_method = password_match_method(senha_informada, senha_hash)
        LOGGER.info("auth login Firebird password_method=%s base_id=%s login=%s", match_method, base_id, login)
        if not verify_database_password(senha_informada, senha_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login ou senha inválidos.")

        nome_usuario = str(usuario_row.get("nome") or login).strip() or login
        nome_empresa = str(empresa_row.get("nomefantasia") or "").strip()
        cnpj = str(empresa_row.get("cgc") or "").strip()
        token_empresa = db_token_empresa
        return self._build_success_response(
            base_id=base_id,
            base_config=base_config,
            company_name=nome_empresa,
            company_cnpj=cnpj,
            token_empresa=token_empresa,
            login=login,
            nome_usuario=nome_usuario,
        )

    def _login_mock(self, payload: dict[str, Any], base_id: str | None) -> dict:
        token = str(payload.get("token") or "")
        login = str(payload.get("login") or "")
        senha = str(payload.get("senha") or "")
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
            "usuario": {
                "login": user_payload["login"],
                "nome": user_payload["nome"],
            },
            "empresa": {
                "base_id": selected_base["id"],
                "nome": company["name"],
                "cnpj": company["cnpj"],
                "token_empresa": company_token,
            },
            "permissoes": {
                "visao_geral": True,
                "vendas": True,
                "financeiro": True,
                "estoque": True,
                "funcionarios": True,
                "configuracoes": True,
            },
            "user": user_payload,
            "company": company,
            "permissions": user_permissions,
        }

    def login(self, payload: dict) -> dict:
        token = payload.get("token") or ""
        base_id = payload.get("base_id")
        company_token, resolved_base_id = self._decode_company_token(token, base_id)
        payload = dict(payload)
        payload["token"] = company_token
        payload["base_id"] = resolved_base_id

        if resolved_base_id:
            try:
                return self._login_real_firebird(payload, company_token, resolved_base_id)
            except HTTPException:
                raise
            except Exception:
                LOGGER.info("Real Firebird validation unavailable, falling back to mock login")
                return self._login_mock(payload, resolved_base_id)

        return self._login_mock(payload, resolved_base_id)

    def me_from_claims(self, claims: dict) -> dict:
        if claims.get("type") != "access":
            raise unauthorized("Token inválido")
        base_id = claims.get("base_id")
        if base_id:
            base_config = self.connection_manager.get_base(base_id)
            if base_config is not None:
                metadata = self.connection_manager.company_metadata(base_config)
                company = {
                    "id": f"company-{claims.get('token_empresa') or claims.get('company_token', '')}",
                    "name": claims.get("nome_empresa") or metadata["nome"],
                    "token": claims.get("token_empresa") or claims.get("company_token", ""),
                    "cnpj": claims.get("cnpj") or metadata["cnpj"],
                    "base_id": base_id,
                    "bases": [
                        {
                            "id": base_id,
                            "name": metadata["nome"],
                            "alias": metadata["nome"].lower().replace(" ", "-"),
                            "host": base_config.get("servidor"),
                            "port": base_config.get("porta"),
                            "charset": "UTF8",
                            "status": "active",
                        }
                    ],
                }
            else:
                company = self.resolve_company(claims.get("company_token", ""), base_id)
        else:
            company = self.resolve_company(claims.get("company_token", ""), base_id)
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
