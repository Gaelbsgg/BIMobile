from pydantic import BaseModel, Field


class EmpresaTokenRequest(BaseModel):
    token: str = Field(min_length=3)


class LoginRequest(BaseModel):
    empresa_token: str
    username: str
    password: str
    base_id: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict
    company: dict

