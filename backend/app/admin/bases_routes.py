from __future__ import annotations

from fastapi import APIRouter, Depends

from app.admin.schemas import BasePayload
from app.admin.service import admin_service
from app.permissions.service import get_permissions_service
from app.core.jwt import get_current_claims


router = APIRouter(prefix="/admin/bases", tags=["admin-bases"])


def require_config_permission():
    return get_permissions_service().dependency_for_module("configuracoes")


@router.get("")
def list_bases(claims: dict = Depends(require_config_permission())):
    return {"items": admin_service.list_bases()}


@router.post("")
def create_base(payload: BasePayload, claims: dict = Depends(require_config_permission())):
    return admin_service.create_base(payload.model_dump())


@router.put("/{base_id}")
def update_base(base_id: str, payload: BasePayload, claims: dict = Depends(require_config_permission())):
    return admin_service.update_base(base_id, payload.model_dump())


@router.delete("/{base_id}")
def delete_base(base_id: str, claims: dict = Depends(require_config_permission())):
    return admin_service.delete_base(base_id)


@router.post("/{base_id}/test-connection")
def test_connection(base_id: str, claims: dict = Depends(require_config_permission())):
    return admin_service.test_connection(base_id)
