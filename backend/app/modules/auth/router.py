from fastapi import APIRouter, Depends

from app.core.security import get_current_claims
from app.modules.auth.schemas import AuthResponse, EmpresaTokenRequest, LoginRequest
from app.modules.auth.service import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/empresa")
def company_token(payload: EmpresaTokenRequest):
    return auth_service.create_company_challenge(payload.token)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return auth_service.login(payload.empresa_token, payload.username, payload.password, payload.base_id)


@router.get("/me")
def me(claims: dict = Depends(get_current_claims)):
    return {
        "user": {
            "id": claims.get("user_id"),
            "name": claims.get("name"),
            "username": claims.get("username"),
            "roles": claims.get("roles", []),
            "permissions": claims.get("permissions", {}),
            "base_id": claims.get("base_id"),
        },
        "company": {
            "id": claims.get("company_id"),
            "token": claims.get("company_token"),
        },
    }
