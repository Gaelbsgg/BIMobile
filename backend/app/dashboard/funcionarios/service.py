from __future__ import annotations

from app.dashboard.funcionarios.queries import FUNCIONARIOS_MOCK


class FuncionariosService:
    def resumo(self, claims: dict) -> dict:
        return {
            "module": "funcionarios",
            "titulo": "Funcionários",
            "base_id": claims.get("base_id"),
            "permissions": claims.get("permissions", {}),
            **FUNCIONARIOS_MOCK["resumo"],
        }


funcionarios_service = FuncionariosService()
