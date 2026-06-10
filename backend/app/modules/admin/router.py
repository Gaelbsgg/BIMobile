from fastapi import APIRouter, Depends

from app.core.dependencies import require_permission
from app.modules.admin.schemas import BasePayload, PermissionPayload
from app.modules.admin.service import admin_service


router = APIRouter(prefix="/admin", tags=["admin"])


def _company_id(claims: dict) -> str:
    return claims.get("company_id", "demo-company")


@router.get("/bases")
def list_bases(claims: dict = Depends(require_permission("configuracoes"))):
    return {"items": admin_service.list_bases(_company_id(claims))}


@router.post("/bases")
def create_base(payload: BasePayload, claims: dict = Depends(require_permission("configuracoes"))):
    return admin_service.create_base(_company_id(claims), payload.model_dump())


@router.put("/bases/{base_id}")
def update_base(base_id: str, payload: BasePayload, claims: dict = Depends(require_permission("configuracoes"))):
    return admin_service.update_base(_company_id(claims), base_id, payload.model_dump())


@router.delete("/bases/{base_id}")
def delete_base(base_id: str, claims: dict = Depends(require_permission("configuracoes"))):
    return admin_service.delete_base(_company_id(claims), base_id)


@router.post("/bases/{base_id}/test-connection")
def test_connection(base_id: str, claims: dict = Depends(require_permission("configuracoes"))):
    return admin_service.test_connection(_company_id(claims), base_id)


@router.get("/permissions")
def list_permissions(claims: dict = Depends(require_permission("configuracoes"))):
    return {"items": admin_service.list_permissions(_company_id(claims))}


@router.put("/permissions/{user_id}")
def update_permissions(user_id: str, payload: PermissionPayload, claims: dict = Depends(require_permission("configuracoes"))):
    return admin_service.update_permissions(_company_id(claims), user_id, payload.model_dump())
