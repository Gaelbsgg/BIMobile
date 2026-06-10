from __future__ import annotations

from fastapi import HTTPException, status

from app.database.base_registry import get_base_registry
from app.database.firebird import test_connection
from app.permissions.service import get_permissions_service


class AdminService:
    def __init__(self):
        self.registry = get_base_registry()
        self.permissions_service = get_permissions_service()

    def list_bases(self) -> list[dict]:
        return [self.registry.public_base(base) for base in self.registry.list_bases()]

    def create_base(self, payload: dict) -> dict:
        return self.registry.public_base(self.registry.create_base(payload))

    def update_base(self, base_id: str, payload: dict) -> dict:
        base = self.registry.get_by_id(base_id)
        if base is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base não encontrada")
        sanitized = {**base, **payload, "id": base_id}
        self.registry.update_base(base_id, sanitized)
        return self.registry.public_base(self.registry.get_by_id(base_id) or sanitized)

    def delete_base(self, base_id: str) -> dict:
        base = self.registry.get_by_id(base_id)
        if base is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base não encontrada")
        self.registry.delete_base(base_id)
        return {"deleted": True, "base_id": base_id}

    def test_connection(self, base_id: str) -> dict:
        base = self.registry.get_by_id(base_id)
        if base is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Base não encontrada")
        return test_connection(base)

    def list_permissions(self, base_id: str) -> dict:
        return {
            "base_id": base_id,
            "items": self.permissions_service.public_permissions_for_base(base_id),
        }

    def update_permissions(self, base_id: str, login: str, payload: dict) -> dict:
        return self.permissions_service.upsert_permission(base_id, login, payload)


admin_service = AdminService()
