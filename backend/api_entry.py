from __future__ import annotations

import uvicorn

from app.config import get_settings
from app.main import app as fastapi_app


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        fastapi_app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
