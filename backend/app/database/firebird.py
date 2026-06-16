from __future__ import annotations

import importlib
from typing import Any


def _load_driver() -> tuple[object | None, str | None]:
    for module_name in ("firebird.driver", "fdb"):
        try:
            driver = importlib.import_module(module_name)
            return driver, module_name
        except Exception:
            continue
    return None, None


def _unavailable_message() -> str:
    return "Nenhum driver Firebird foi encontrado. Instale firebird-driver ou fdb para habilitar a conexão real."


def get_connection(base_config: dict[str, Any]):
    driver, _driver_name = _load_driver()
    if driver is None:
        raise RuntimeError(_unavailable_message())

    servidor = base_config.get("servidor") or base_config.get("host") or "127.0.0.1"
    porta = int(base_config.get("porta") or base_config.get("port") or 3050)
    caminho_fdb = base_config.get("caminho_fdb") or base_config.get("path") or ""
    usuario = base_config.get("usuario_firebird") or base_config.get("username") or "sysdba"
    senha = base_config.get("senha_firebird") or base_config.get("password") or "masterkey"
    charset = base_config.get("charset") or "UTF8"

    if hasattr(driver, "connect"):
        return driver.connect(
            dsn=f"{servidor}/{porta}:{caminho_fdb}",
            user=usuario,
            password=senha,
            charset=charset,
        )

    return driver.create_database(
        dsn=f"{servidor}/{porta}:{caminho_fdb}",
        user=usuario,
        password=senha,
        charset=charset,
    )


def test_connection(base_config: dict[str, Any]) -> dict[str, Any]:
    driver, driver_name = _load_driver()
    if driver is None:
        return {
            "ok": False,
            "mode": "unavailable",
            "message": _unavailable_message(),
            "base_id": base_config.get("id"),
        }

    try:
        conn = get_connection(base_config)
        if hasattr(conn, "close"):
            conn.close()
        return {
            "ok": True,
            "mode": "real",
            "message": f"Conexão com Firebird validada com sucesso usando {driver_name}.",
            "base_id": base_config.get("id"),
        }
    except Exception as exc:
        return {
            "ok": False,
            "mode": "real",
            "message": f"Falha ao conectar no Firebird usando {driver_name or 'driver'}: {exc}",
            "base_id": base_config.get("id"),
        }


def execute_query(base_config: dict[str, Any], sql: str, params: dict[str, Any] | tuple[Any, ...] | None = None) -> list[dict[str, Any]]:
    driver, _driver_name = _load_driver()
    if driver is None:
        return []

    conn = get_connection(base_config)
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params or ())
        columns = [column[0].lower() for column in cursor.description] if cursor.description else []
        rows = cursor.fetchall() or []
        return [dict(zip(columns, row)) for row in rows]
    finally:
        if hasattr(conn, "close"):
            conn.close()
