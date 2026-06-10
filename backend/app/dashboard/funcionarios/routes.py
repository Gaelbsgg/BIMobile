from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.funcionarios.schemas import FuncionariosResumoResponse
from app.dashboard.funcionarios.service import funcionarios_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/funcionarios", tags=["dashboard-funcionarios"])


def require_access():
    return get_permissions_service().dependency_for_module("funcionarios")


@router.get("", response_model=FuncionariosResumoResponse)
def root(claims: dict = Depends(require_access())):
    return funcionarios_service.resumo(claims)


@router.get("/resumo", response_model=FuncionariosResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return funcionarios_service.resumo(claims)
