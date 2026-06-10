from __future__ import annotations

from fastapi import HTTPException, status

from app.services.local_config_store import get_store


class DashboardService:
    def _claims_to_permissions(self, claims: dict) -> dict:
        return claims.get("permissions", {})

    def _ensure_permission(self, claims: dict, module: str) -> None:
        permissions = self._claims_to_permissions(claims)
        if module not in permissions.get("modules", []) and "admin" not in claims.get("roles", []):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão para este módulo")

    def _base_context(self, claims: dict) -> dict:
        store = get_store().read()
        company = next((item for item in store.get("companies", []) if item["id"] == claims.get("company_id")), {})
        base_id = claims.get("base_id")
        base = next((item for item in company.get("bases", []) if item["id"] == base_id), company.get("bases", [{}])[0])
        return {"company": company, "base": base}

    def overview(self, claims: dict) -> dict:
        self._ensure_permission(claims, "overview")
        context = self._base_context(claims)
        return {
            "module": "overview",
            "title": "Visão Geral",
            "company": context["company"].get("name"),
            "base": context["base"].get("name"),
            "kpis": [
                {"label": "Vendas", "value": "R$ 248.430", "delta": "+12,4%", "key": "vendas"},
                {"label": "Pedidos", "value": "1.284", "delta": "+5,1%", "key": "pedidos"},
                {"label": "Margem", "value": "31,8%", "delta": "+1,7%", "key": "margem"},
                {"label": "Estoque", "value": "92%", "delta": "-0,8%", "key": "estoque"},
            ],
            "charts": [
                {
                    "type": "area",
                    "title": "Faturamento mensal",
                    "data": [
                        {"name": "Jan", "value": 180},
                        {"name": "Fev", "value": 220},
                        {"name": "Mar", "value": 190},
                        {"name": "Abr", "value": 260},
                        {"name": "Mai", "value": 320},
                        {"name": "Jun", "value": 310},
                    ],
                }
            ],
            "filters": {
                "periods": ["Hoje", "7 dias", "30 dias", "90 dias"],
                "companies": [context["company"].get("name")],
                "bases": [context["base"].get("name")],
            },
        }

    def vendas(self, claims: dict) -> dict:
        self._ensure_permission(claims, "vendas")
        return {
            "module": "vendas",
            "title": "Vendas",
            "kpis": [
                {"label": "Faturamento", "value": "R$ 124.900", "delta": "+9,8%", "key": "faturamento"},
                {"label": "Conversão", "value": "18,2%", "delta": "+0,9%", "key": "conversao"},
            ],
            "charts": [
                {
                    "type": "bar",
                    "title": "Vendas por canal",
                    "data": [
                        {"name": "Loja", "value": 84},
                        {"name": "WhatsApp", "value": 52},
                        {"name": "Representantes", "value": 36},
                    ],
                }
            ],
        }

    def financeiro(self, claims: dict) -> dict:
        self._ensure_permission(claims, "financeiro")
        return {
            "module": "financeiro",
            "title": "Financeiro",
            "kpis": [
                {"label": "Recebimentos", "value": "R$ 98.120", "delta": "+7,2%", "key": "recebimentos"},
                {"label": "Inadimplência", "value": "2,4%", "delta": "-0,3%", "key": "inadimplencia"},
            ],
            "charts": [
                {
                    "type": "line",
                    "title": "Fluxo de caixa",
                    "data": [
                        {"name": "Sem 1", "value": 80},
                        {"name": "Sem 2", "value": 74},
                        {"name": "Sem 3", "value": 91},
                        {"name": "Sem 4", "value": 88},
                    ],
                }
            ],
        }

    def estoque(self, claims: dict) -> dict:
        self._ensure_permission(claims, "estoque")
        return {
            "module": "estoque",
            "title": "Estoque",
            "kpis": [
                {"label": "SKUs", "value": "3.482", "delta": "+2,1%", "key": "skus"},
                {"label": "Ruptura", "value": "1,1%", "delta": "-0,4%", "key": "ruptura"},
            ],
            "charts": [
                {
                    "type": "area",
                    "title": "Cobertura de estoque",
                    "data": [
                        {"name": "A", "value": 35},
                        {"name": "B", "value": 52},
                        {"name": "C", "value": 48},
                        {"name": "D", "value": 61},
                    ],
                }
            ],
        }

    def funcionarios(self, claims: dict) -> dict:
        self._ensure_permission(claims, "funcionarios")
        return {
            "module": "funcionarios",
            "title": "Funcionários",
            "kpis": [
                {"label": "Ativos", "value": "128", "delta": "+4", "key": "ativos"},
                {"label": "Turnover", "value": "3,2%", "delta": "-0,7%", "key": "turnover"},
            ],
            "charts": [
                {
                    "type": "bar",
                    "title": "Produtividade por equipe",
                    "data": [
                        {"name": "Comercial", "value": 78},
                        {"name": "Financeiro", "value": 61},
                        {"name": "Logística", "value": 69},
                    ],
                }
            ],
        }


dashboard_service = DashboardService()
