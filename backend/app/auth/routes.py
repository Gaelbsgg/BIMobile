from __future__ import annotations

from fastapi import APIRouter, Depends

from app.auth.schemas import AuthResponse, EmpresaTokenRequest, LoginRequest
from app.auth.service import auth_service
from app.core.jwt import get_current_claims


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/empresa")
def empresa(payload: EmpresaTokenRequest):
    return auth_service.create_company_challenge(payload.token)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return auth_service.login(payload.normalized())


@router.get("/me")
def me(claims: dict = Depends(get_current_claims)):
    return auth_service.me_from_claims(claims)


@router.post("/logout")
def logout(claims: dict = Depends(get_current_claims)):
    return {"success": True, "message": "Logout realizado com sucesso", "user": claims.get("login")}
