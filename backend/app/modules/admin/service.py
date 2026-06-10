from __future__ import annotations

from fastapi import HTTPException, status

from app.services.database_service import database_service
from app.services.local_config_store import get_store


class AdminService:
    def _get_company(self, company_id: str) -> dict:
        data = get_store().read()
        company = next((item for item in data.get("companies", []) if item["id"] == company_id), None)
        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
        return company

    def list_bases(self, company_id: str) -> list[dict]:
        return self._get_company(company_id).get("bases", [])

    def create_base(self, company_id: str, payload: dict) -> dict:
        def updater(data):
            company = next((item for item in data.get("companies", []) if item["id"] == company_id), None)
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
            new_base = {"id": f"base-{len(company.get('bases', [])) + 1}", **payload}
            company.setdefault("bases", []).append(new_base)
            return data

        updated = get_store().update(updater)
        company = next((item for item in updated.get("companies", []) if item["id"] == company_id), None)
        return company["bases"][-1]

    def update_base(self, company_id: str, base_id: str, payload: dict) -> dict:
        def updater(data):
            company = next((item for item in data.get("companies", []) if item["id"] == company_id), None)
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
            base = next((item for item in company.get("bases", []) if item["id"] == base_id), None)
            if base is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base não encontrada")
            base.update(payload)
            return data

        updated = get_store().update(updater)
        company = next((item for item in updated.get("companies", []) if item["id"] == company_id), None)
        return next(base for base in company["bases"] if base["id"] == base_id)

    def delete_base(self, company_id: str, base_id: str) -> dict:
        def updater(data):
            company = next((item for item in data.get("companies", []) if item["id"] == company_id), None)
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
            company["bases"] = [base for base in company.get("bases", []) if base["id"] != base_id]
            return data

        get_store().update(updater)
        return {"deleted": True, "base_id": base_id}

    def test_connection(self, company_id: str, base_id: str) -> dict:
        base = next((item for item in self.list_bases(company_id) if item["id"] == base_id), None)
        if base is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base não encontrada")
        return database_service.test_connection(base)

    def list_permissions(self, company_id: str) -> list[dict]:
        company = self._get_company(company_id)
        return [
            {
                "user_id": user["id"],
                "name": user["name"],
                "username": user["username"],
                "roles": user.get("roles", []),
                "permissions": user.get("permissions", {}),
            }
            for user in company.get("users", [])
        ]

    def update_permissions(self, company_id: str, user_id: str, payload: dict) -> dict:
        def updater(data):
            company = next((item for item in data.get("companies", []) if item["id"] == company_id), None)
            if company is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
            user = next((item for item in company.get("users", []) if item["id"] == user_id), None)
            if user is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
            user["permissions"] = payload
            return data

        get_store().update(updater)
        return {
            "user_id": user_id,
            "permissions": payload,
        }


admin_service = AdminService()
