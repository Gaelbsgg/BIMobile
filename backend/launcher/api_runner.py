from __future__ import annotations

import json
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

_process: subprocess.Popen[str] | None = None
_lock = threading.Lock()


def _launcher_path() -> Path:
    return Path(__file__).resolve().with_name("desktop_launcher.py")


def _api_command() -> list[str]:
    if getattr(sys, "frozen", False):
        return [sys.executable, "--api"]
    return [sys.executable, str(_launcher_path()), "--api"]


def _api_headers() -> dict[str, str]:
    return {"Accept": "application/json"}


def test_health(timeout: float = 2.0) -> dict[str, object]:
    request = urllib.request.Request("http://127.0.0.1:8000/health", headers=_api_headers())
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return {"ok": True, "message": "API respondendo com sucesso.", "data": payload}
    except urllib.error.URLError as exc:
        return {"ok": False, "message": f"API indisponível: {exc}"}
    except Exception as exc:
        return {"ok": False, "message": f"Falha ao testar a API: {exc}"}


def is_api_running() -> bool:
    global _process
    if _process is not None and _process.poll() is None:
        return True
    health = test_health(timeout=1.0)
    return bool(health.get("ok"))


def start_api() -> dict[str, object]:
    global _process
    with _lock:
        if is_api_running():
            return {"ok": True, "message": "A API já está em execução.", "running": True}

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        try:
            _process = subprocess.Popen(
                _api_command(),
                cwd=str(Path(__file__).resolve().parents[1]),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
            )
        except Exception as exc:
            _process = None
            return {"ok": False, "message": f"Falha ao iniciar a API: {exc}", "running": False}

    deadline = time.time() + 20
    last_health = {"ok": False, "message": "Aguardando inicialização da API..."}
    while time.time() < deadline:
        last_health = test_health(timeout=1.0)
        if last_health.get("ok"):
            return {"ok": True, "message": "API iniciada com sucesso.", "running": True}
        time.sleep(0.5)

    return {
        "ok": False,
        "message": last_health.get("message", "Não foi possível validar o início da API."),
        "running": False,
    }


def stop_api() -> dict[str, object]:
    global _process
    with _lock:
        if _process is None:
            return {"ok": False, "message": "Nenhuma instância da API foi iniciada por este gerenciador.", "running": False}
        if _process.poll() is not None:
            _process = None
            return {"ok": True, "message": "API já estava parada.", "running": False}

        _process.terminate()
        try:
            _process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            _process.kill()
            _process.wait(timeout=5)
        finally:
            _process = None

    return {"ok": True, "message": "API parada com sucesso.", "running": False}


def open_docs() -> None:
    webbrowser.open("http://127.0.0.1:8000/docs")
