from fastapi import Depends, HTTPException, status

from app.core.security import get_current_claims


def require_permission(permission: str):
    def dependency(claims: dict = Depends(get_current_claims)) -> dict:
        permissions = claims.get("permissions", {})
        modules = permissions.get("modules", [])
        if permission not in modules and "admin" not in claims.get("roles", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")
        return claims

    return dependency
