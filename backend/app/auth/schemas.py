from __future__ import annotations

from pydantic import BaseModel, Field


class EmpresaTokenRequest(BaseModel):
    token: str = Field(min_length=1)


class LoginRequest(BaseModel):
    token: str | None = None
    empresa_token: str | None = None
    login: str | None = None
    username: str | None = None
    senha: str | None = None
    password: str | None = None
    base_id: str | None = None

    def normalized(self) -> dict:
        token = self.token or self.empresa_token or ""
        login = self.login or self.username or ""
        senha = self.senha or self.password or ""
        return {
            "token": token,
            "empresa_token": self.empresa_token or self.token or "",
            "login": login,
            "username": self.username or self.login or "",
            "senha": senha,
            "password": self.password or self.senha or "",
            "base_id": self.base_id,
        }


class BasePublicSchema(BaseModel):
    id: str
    name: str
    alias: str | None = None
    host: str | None = None
    port: int | None = None
    charset: str | None = None
    status: str | None = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    token: str
    cnpj: str
    base_id: str
    bases: list[BasePublicSchema] = Field(default_factory=list)


class AuthUserResponse(BaseModel):
    id: str
    login: str
    nome: str
    name: str
    username: str
    roles: list[str] = Field(default_factory=list)
    permissions: dict = Field(default_factory=dict)
    base_id: str | None = None


class UsuarioLoginResponse(BaseModel):
    login: str
    nome: str


class EmpresaLoginResponse(BaseModel):
    base_id: str
    nome: str
    cnpj: str
    token_empresa: str


class PermissoesLoginResponse(BaseModel):
    visao_geral: bool = True
    vendas: bool = True
    financeiro: bool = True
    estoque: bool = True
    funcionarios: bool = True
    configuracoes: bool = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioLoginResponse
    empresa: EmpresaLoginResponse
    permissoes: PermissoesLoginResponse
    user: AuthUserResponse
    company: CompanyResponse
    permissions: dict = Field(default_factory=dict)
