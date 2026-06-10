from __future__ import annotations

from pydantic import BaseModel


class FuncionariosResumoResponse(BaseModel):
    ativos: int
    turnover: float
    admitidos_periodo: int

