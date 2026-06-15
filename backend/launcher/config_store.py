from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


class ConfigStore:
    def __init__(self, data_dir: str | Path | None = None):
        self.root_dir = _runtime_root()
        self.data_dir = Path(data_dir) if data_dir else self.root_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bases_path = self.data_dir / "bases_config.json"
        self.permissions_path = self.data_dir / "permissions_config.json"
        self._ensure_defaults()

    def _bundled_file(self, filename: str) -> Path | None:
        candidates = []
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / "data" / filename)  # type: ignore[attr-defined]
        candidates.append(Path(__file__).resolve().parents[1] / "data" / filename)
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _read_json(self, path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return default
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_json(self, path: Path, data: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def _ensure_defaults(self) -> None:
        if not self.bases_path.exists():
            bundled = self._bundled_file("bases_config.json")
            if bundled is not None:
                self.bases_path.write_text(bundled.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                self._write_json(self.bases_path, {"bases": [], "selecionar_base_ao_iniciar": False})

        if not self.permissions_path.exists():
            bundled = self._bundled_file("permissions_config.json")
            if bundled is not None:
                self.permissions_path.write_text(bundled.read_text(encoding="utf-8"), encoding="utf-8")
            else:
                self._write_json(self.permissions_path, {"bases": {}})

    def load_bases_config(self) -> dict[str, Any]:
        data = self._read_json(self.bases_path, {"bases": [], "selecionar_base_ao_iniciar": False})
        bases = []
        for base in data.get("bases", []):
            bases.append(self.normalize_base(base))
        return {
            "bases": bases,
            "selecionar_base_ao_iniciar": bool(data.get("selecionar_base_ao_iniciar", False)),
        }

    def save_bases_config(self, bases: list[dict[str, Any]], selecionar_base_ao_iniciar: bool = False) -> None:
        normalized = [self.normalize_base(base) for base in bases]
        selected = next((base for base in normalized if base.get("base_padrao")), None)
        if selected is not None:
            for base in normalized:
                base["base_padrao"] = base.get("id") == selected.get("id")
        self._write_json(
            self.bases_path,
            {
                "bases": normalized,
                "selecionar_base_ao_iniciar": bool(selecionar_base_ao_iniciar),
            },
        )

    def normalize_base(self, base: dict[str, Any]) -> dict[str, Any]:
        descricao = base.get("descricao") or base.get("nome_configuracao") or base.get("apelido") or "Nova Base"
        apelido = base.get("apelido") or descricao
        caminho_base = base.get("caminho_base") or ""
        nome_arquivo = base.get("nome_arquivo") or ""
        caminho_fdb = base.get("caminho_fdb") or ""

        if caminho_fdb and not caminho_base:
            caminho_base = str(Path(caminho_fdb).parent) + os.sep
        if caminho_fdb and not nome_arquivo:
            nome_arquivo = Path(caminho_fdb).name
        if not caminho_fdb and caminho_base and nome_arquivo:
            caminho_fdb = str(Path(caminho_base) / nome_arquivo)

        return {
            "id": base.get("id") or "",
            "apelido": apelido,
            "descricao": descricao,
            "servidor": base.get("servidor") or base.get("host") or "localhost",
            "porta": int(base.get("porta") or base.get("port") or 3050),
            "caminho_base": caminho_base,
            "nome_arquivo": nome_arquivo,
            "caminho_fdb": caminho_fdb,
            "usuario_firebird": base.get("usuario_firebird") or base.get("username") or "SYSDBA",
            "senha_firebird": base.get("senha_firebird") or base.get("password") or "masterkey",
            "protocolo": base.get("protocolo") or "TCP-IP",
            "servidor_linux": bool(base.get("servidor_linux", False)),
            "ativo": bool(base.get("ativo", True)),
            "base_padrao": bool(base.get("base_padrao", False)),
            "token_empresa": base.get("token_empresa", ""),
        }

    def upsert_base(self, base: dict[str, Any]) -> dict[str, Any]:
        config = self.load_bases_config()
        bases = config["bases"]
        normalized = self.normalize_base(base)
        if not str(normalized.get("id") or "").strip():
            existing_ids = {str(item.get("id")) for item in bases}
            next_index = 1
            while f"base_{next_index:03d}" in existing_ids:
                next_index += 1
            normalized["id"] = f"base_{next_index:03d}"
        existing = next((item for item in bases if item.get("id") == normalized.get("id")), None)
        if existing is None:
            bases.append(normalized)
        else:
            existing.update(normalized)
        if normalized.get("base_padrao"):
            for item in bases:
                item["base_padrao"] = item.get("id") == normalized.get("id")
        self.save_bases_config(bases, config.get("selecionar_base_ao_iniciar", False))
        return normalized

    def delete_base(self, base_id: str) -> None:
        config = self.load_bases_config()
        bases = [base for base in config["bases"] if base.get("id") != base_id]
        self.save_bases_config(bases, config.get("selecionar_base_ao_iniciar", False))

    def set_default(self, base_id: str) -> None:
        config = self.load_bases_config()
        bases = config["bases"]
        for base in bases:
            base["base_padrao"] = base.get("id") == base_id
        self.save_bases_config(bases, config.get("selecionar_base_ao_iniciar", False))

    def set_select_on_start(self, enabled: bool) -> None:
        config = self.load_bases_config()
        self.save_bases_config(config["bases"], enabled)

    def get_base(self, base_id: str) -> dict[str, Any] | None:
        return next((base for base in self.load_bases_config()["bases"] if base.get("id") == base_id), None)

    def list_bases(self) -> list[dict[str, Any]]:
        return self.load_bases_config()["bases"]
