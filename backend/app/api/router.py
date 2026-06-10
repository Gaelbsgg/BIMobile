from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.admin.router import router as admin_router
from app.modules.dashboard.router import router as dashboard_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(dashboard_router)
