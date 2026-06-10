from __future__ import annotations

from fastapi import APIRouter, Depends

from app.admin.schemas import PermissionPayload
from app.admin.service import admin_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/admin/permissions", tags=["admin-permissions"])


def require_config_permission():
    return get_permissions_service().dependency_for_module("configuracoes")


@router.get("/{base_id}")
def list_permissions(base_id: str, claims: dict = Depends(require_config_permission())):
    return admin_service.list_permissions(base_id)


@router.put("/{base_id}/{login}")
def update_permissions(base_id: str, login: str, payload: PermissionPayload, claims: dict = Depends(require_config_permission())):
    return admin_service.update_permissions(base_id, login, payload.model_dump())
