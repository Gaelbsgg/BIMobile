from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_CONFIG: dict[str, Any] = {
    "app": {
        "name": "BIMobile",
        "company": "ResultBI",
        "version": "0.1.0",
    },
    "api": {
        "host": "127.0.0.1",
        "port": 8000,
        "exe": "BIMobileAPI.exe",
        "docs_url": "http://127.0.0.1:8000/docs",
        "health_url": "http://127.0.0.1:8000/health",
    },
    "service": {
        "name": "BIMobileAPI",
        "display_name": "ResultBI BIMobile API",
        "description": "Serviço local da API BIMobile para conexão com Firebird",
    },
    "paths": {
        "data": "../data",
        "logs": "../logs",
        "bases_config": "../data/bases_config.json",
        "permissions_config": "../data/permissions_config.json",
    },
    "cloudflared": {
        "enabled": False,
        "exe": "cloudflared.exe",
        "tunnel_url": "",
    },
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_config_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "config.json"
    return _backend_root() / "bin" / "config.json"


def candidate_runtime_config_paths() -> list[Path]:
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        candidates.append(Path(sys.executable).resolve().parent / "config.json")
    candidates.extend(
        [
            Path.cwd() / "config.json",
            _backend_root() / "bin" / "config.json",
            _backend_root() / "config.json",
            _repo_root() / "config.json",
        ]
    )

    unique: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = str(candidate.resolve() if candidate.exists() else candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def find_runtime_config_path() -> Path:
    for candidate in candidate_runtime_config_paths():
        if candidate.exists():
            return candidate
    return _default_config_path()


def _merge_dicts(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dicts(merged[key], value)  # type: ignore[arg-type]
        else:
            merged[key] = value
    return merged


@lru_cache
def load_runtime_config() -> dict[str, Any]:
    path = find_runtime_config_path()
    if path.exists():
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except Exception:
            payload = {}
    else:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    return _merge_dicts(DEFAULT_RUNTIME_CONFIG, payload)


def runtime_config_path() -> Path:
    return find_runtime_config_path()


def runtime_base_dir() -> Path:
    return runtime_config_path().resolve().parent


def resolve_runtime_path(relative_path: str | None) -> Path:
    if not relative_path:
        return runtime_base_dir()
    candidate = Path(relative_path)
    if candidate.is_absolute():
        return candidate
    return (runtime_base_dir() / candidate).resolve()
