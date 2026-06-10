from __future__ import annotations

from app.modules.admin.service import admin_service


class PermissionService:
    def list_company_permissions(self, company_id: str) -> list[dict]:
        return admin_service.list_permissions(company_id)

    def update_user_permissions(self, company_id: str, user_id: str, payload: dict) -> dict:
        return admin_service.update_permissions(company_id, user_id, payload)

    def can_access(self, claims: dict, module: str) -> bool:
        if "admin" in claims.get("roles", []):
            return True
        return module in claims.get("permissions", {}).get("modules", [])


permission_service = PermissionService()
