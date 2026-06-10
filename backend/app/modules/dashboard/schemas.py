from pydantic import BaseModel


class DashboardResponse(BaseModel):
    module: str
    kpis: list[dict]
    charts: list[dict]
    filters: dict

