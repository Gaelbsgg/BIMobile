from __future__ import annotations

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.passwords import verify_password
from app.core.security import create_token, decode_token
from app.services.local_config_store import get_store


class AuthService:
    def get_company_by_token(self, token: str) -> dict:
        companies = get_store().read().get("companies", [])
        for company in companies:
            if company["token"] == token and company.get("status") == "active":
                return company
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token da empresa inválido")

    def create_company_challenge(self, token: str) -> dict:
        company = self.get_company_by_token(token)
        settings = get_settings()
        empresa_token = create_token(
            {
                "type": "company_challenge",
                "company_id": company["id"],
                "company_token": company["token"],
            },
            settings.company_token_expire_minutes,
        )
        return {
            "empresa_token": empresa_token,
            "company": {
                "id": company["id"],
                "name": company["name"],
                "token": company["token"],
                "bases": [
                    {
                        "id": base["id"],
                        "name": base["name"],
                        "alias": base.get("alias"),
                        "host": base.get("host"),
                        "port": base.get("port"),
                        "charset": base.get("charset"),
                        "status": base.get("status"),
                    }
                    for base in company.get("bases", [])
                ],
            },
        }

    def login(self, empresa_token: str, username: str, password: str, base_id: str | None = None) -> dict:
        challenge = decode_token(empresa_token)
        if challenge.get("type") != "company_challenge":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Fluxo de empresa inválido")

        company = self.get_company_by_token(challenge["company_token"])
        users = company.get("users", [])
        user = next((item for item in users if item["username"].lower() == username.lower()), None)
        if user is None or not verify_password(password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")

        selected_base = None
        if company.get("bases"):
            selected_base = next((base for base in company["bases"] if base["id"] == base_id), company["bases"][0])

        settings = get_settings()
        access_token = create_token(
            {
                "type": "access",
                "company_id": company["id"],
                "company_token": company["token"],
                "base_id": selected_base["id"] if selected_base else None,
                "user_id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "roles": user.get("roles", []),
                "permissions": user.get("permissions", {}),
            },
            settings.access_token_expire_minutes,
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "roles": user.get("roles", []),
                "permissions": user.get("permissions", {}),
                "base_id": selected_base["id"] if selected_base else None,
            },
            "company": {
                "id": company["id"],
                "name": company["name"],
                "token": company["token"],
                "bases": company.get("bases", []),
            },
        }


auth_service = AuthService()
