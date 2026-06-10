from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.financeiro.schemas import FinanceiroListResponse, FinanceiroResumoResponse
from app.dashboard.financeiro.service import financeiro_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/financeiro", tags=["dashboard-financeiro"])


def require_access():
    return get_permissions_service().dependency_for_module("financeiro")


@router.get("", response_model=FinanceiroResumoResponse)
def root(claims: dict = Depends(require_access())):
    return financeiro_service.resumo(claims)


@router.get("/resumo", response_model=FinanceiroResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return financeiro_service.resumo(claims)


@router.get("/contas-receber", response_model=FinanceiroListResponse)
def contas_receber(claims: dict = Depends(require_access())):
    return financeiro_service.contas_receber(claims)


@router.get("/contas-pagar", response_model=FinanceiroListResponse)
def contas_pagar(claims: dict = Depends(require_access())):
    return financeiro_service.contas_pagar(claims)
