from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dashboard.overview.schemas import OverviewResumoResponse
from app.dashboard.overview.service import overview_service
from app.permissions.service import get_permissions_service


router = APIRouter(prefix="/dashboard/overview", tags=["dashboard-overview"])


def require_access():
    return get_permissions_service().dependency_for_module("overview")


@router.get("", response_model=OverviewResumoResponse)
def root(claims: dict = Depends(require_access())):
    return overview_service.resumo(claims)


@router.get("/resumo", response_model=OverviewResumoResponse)
def resumo(claims: dict = Depends(require_access())):
    return overview_service.resumo(claims)
