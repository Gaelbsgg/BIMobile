from __future__ import annotations

from pathlib import Path
from typing import Any


class DatabaseService:
    def test_connection(self, base: dict[str, Any]) -> dict[str, Any]:
        path = Path(base.get("path", ""))
        simulated_ok = base.get("status") == "mock"
        file_exists = path.exists()
        ok = simulated_ok or file_exists
        return {
            "ok": ok,
            "base_id": base.get("id"),
            "message": "Conexão simulada com sucesso" if ok else "Arquivo .FDB não encontrado",
            "mode": "mock" if simulated_ok else "filesystem-check",
        }


database_service = DatabaseService()
