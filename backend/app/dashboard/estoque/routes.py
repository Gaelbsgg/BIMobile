from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.estoque.schemas import EstoqueListResponse, EstoqueResumoResponse
from app.dashboard.estoque.service import estoque_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/estoque", tags=["dashboard-estoque"])


def require_access():
    return get_permissions_service().dependency_for_module("estoque")


@router.get("", response_model=EstoqueResumoResponse)
def root(claims: dict = Depends(require_access())):
    return estoque_service.resumo(claims)


@router.get("/resumo", response_model=EstoqueResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return estoque_service.resumo(claims)


@router.get("/baixo-minimo", response_model=EstoqueListResponse)
def baixo_minimo(claims: dict = Depends(require_access())):
    return estoque_service.baixo_minimo(claims)
