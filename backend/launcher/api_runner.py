from __future__ import annotations

import json
import urllib.error
import urllib.request
import webbrowser

from app.config import get_settings


def _api_headers() -> dict[str, str]:
    return {"Accept": "application/json"}


def _health_url() -> str:
    return get_settings().health_url


def _docs_url() -> str:
    return get_settings().docs_url


def test_health(timeout: float = 2.0) -> dict[str, object]:
    request = urllib.request.Request(_health_url(), headers=_api_headers())
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {"ok": True, "message": "API respondendo com sucesso.", "data": payload}
    except urllib.error.URLError as exc:
        return {"ok": False, "message": f"API indisponível: {exc}"}
    except Exception as exc:
        return {"ok": False, "message": f"Falha ao testar a API: {exc}"}


def open_docs() -> None:
    webbrowser.open(_docs_url())
