from fastapi import APIRouter

from app.admin.bases_routes import router as admin_bases_router
from app.admin.permissions_routes import router as admin_permissions_router
from app.auth.routes import router as auth_router
from app.dashboard.estoque.routes import router as dashboard_estoque_router
from app.dashboard.configuracoes.routes import router as dashboard_configuracoes_router
from app.dashboard.financeiro.routes import router as dashboard_financeiro_router
from app.dashboard.funcionarios.routes import router as dashboard_funcionarios_router
from app.dashboard.overview.routes import router as dashboard_overview_router
from app.dashboard.vendas.routes import router as dashboard_vendas_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(admin_bases_router)
api_router.include_router(admin_permissions_router)
api_router.include_router(dashboard_overview_router)
api_router.include_router(dashboard_vendas_router)
api_router.include_router(dashboard_financeiro_router)
api_router.include_router(dashboard_estoque_router)
api_router.include_router(dashboard_funcionarios_router)
api_router.include_router(dashboard_configuracoes_router)
