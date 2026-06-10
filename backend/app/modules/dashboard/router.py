from fastapi import APIRouter, Depends

from app.core.security import get_current_claims
from app.modules.dashboard.service import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def overview(claims: dict = Depends(get_current_claims)):
    return dashboard_service.overview(claims)


@router.get("/vendas")
def vendas(claims: dict = Depends(get_current_claims)):
    return dashboard_service.vendas(claims)


@router.get("/financeiro")
def financeiro(claims: dict = Depends(get_current_claims)):
    return dashboard_service.financeiro(claims)


@router.get("/estoque")
def estoque(claims: dict = Depends(get_current_claims)):
    return dashboard_service.estoque(claims)


@router.get("/funcionarios")
def funcionarios(claims: dict = Depends(get_current_claims)):
    return dashboard_service.funcionarios(claims)
