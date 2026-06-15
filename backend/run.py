from __future__ import annotations

import os
import sys

import uvicorn


if __name__ == "__main__":
    is_frozen = getattr(sys, "frozen", False)
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload_flag = False if is_frozen else os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("app.main:app", host=host, port=port, reload=reload_flag)
