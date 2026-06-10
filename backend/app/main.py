from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.bases_routes import router as admin_bases_router
from app.admin.permissions_routes import router as admin_permissions_router
from app.auth.routes import router as auth_router
from app.config import get_settings
from app.dashboard.estoque.routes import router as dashboard_estoque_router
from app.dashboard.configuracoes.routes import router as dashboard_configuracoes_router
from app.dashboard.financeiro.routes import router as dashboard_financeiro_router
from app.dashboard.funcionarios.routes import router as dashboard_funcionarios_router
from app.dashboard.overview.routes import router as dashboard_overview_router
from app.dashboard.vendas.routes import router as dashboard_vendas_router


settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_bases_router)
app.include_router(admin_permissions_router)
app.include_router(dashboard_overview_router)
app.include_router(dashboard_vendas_router)
app.include_router(dashboard_financeiro_router)
app.include_router(dashboard_estoque_router)
app.include_router(dashboard_funcionarios_router)
app.include_router(dashboard_configuracoes_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
