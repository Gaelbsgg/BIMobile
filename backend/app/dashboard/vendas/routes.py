from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.vendas.schemas import VendasListResponse, VendasResumoResponse
from app.dashboard.vendas.service import vendas_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/vendas", tags=["dashboard-vendas"])


def require_access():
    return get_permissions_service().dependency_for_module("vendas")


@router.get("", response_model=VendasResumoResponse)
def root(claims: dict = Depends(require_access())):
    return vendas_service.resumo(claims)


@router.get("/resumo", response_model=VendasResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return vendas_service.resumo(claims)


@router.get("/top-produtos", response_model=VendasListResponse)
def top_produtos(claims: dict = Depends(require_access())):
    return vendas_service.top_produtos(claims)


@router.get("/por-vendedor", response_model=VendasListResponse)
def por_vendedor(claims: dict = Depends(require_access())):
    return vendas_service.por_vendedor(claims)
