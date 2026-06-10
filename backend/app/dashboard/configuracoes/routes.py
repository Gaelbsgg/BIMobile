from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.configuracoes.schemas import ConfiguracoesResumoResponse
from app.dashboard.configuracoes.service import configuracoes_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/configuracoes", tags=["dashboard-configuracoes"])


def require_access():
    return get_permissions_service().dependency_for_module("configuracoes")


@router.get("", response_model=ConfiguracoesResumoResponse)
def root(claims: dict = Depends(require_access())):
    return configuracoes_service.resumo(claims)


@router.get("/resumo", response_model=ConfiguracoesResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return configuracoes_service.resumo(claims)
