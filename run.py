"""Convenience launcher for the CHRONOS-SAFE web interface."""

from __future__ import annotations

import os
<<<<<<< HEAD
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parent / "chronos_safe"
    os.chdir(project_root)
    sys.path.insert(0, str(project_root))

    from chronos_safe.runtime import run_web_server

    run_web_server()
=======
import threading
import webbrowser

from chronos_safe.config.settings import SETTINGS
from chronos_safe.utils.logging_utils import configure_logging


def _ensure_runtime_directories() -> None:
    for path in (
        SETTINGS.data_root,
        SETTINGS.data_root / "raw",
        SETTINGS.data_root / "processed",
        SETTINGS.data_root / "cache",
        SETTINGS.data_root / "fixtures",
        SETTINGS.models_root,
        SETTINGS.models_root / "checkpoints",
        SETTINGS.models_root / "scalers",
        SETTINGS.reports_root,
        SETTINGS.reports_root / "figures",
        SETTINGS.reports_root / "benchmarks",
        SETTINGS.reports_root / "validation",
    ):
        path.mkdir(parents=True, exist_ok=True)


def main() -> None:
    try:
        # pyrefly: ignore [missing-import]
        import uvicorn
    except ImportError as exc:  # pragma: no cover - runtime dependency error
        raise RuntimeError(
            "uvicorn is required to run the web UI. Install with: python -m pip install -e ."
        ) from exc

    configure_logging(SETTINGS.log_level)
    _ensure_runtime_directories()

    render_port = os.getenv("PORT")
    host = os.getenv("CHRONOS_HOST", "0.0.0.0" if render_port else "127.0.0.1")
    port = int(render_port or os.getenv("CHRONOS_PORT", "8000"))
    default_open_browser = "false" if render_port else "true"
    open_browser = os.getenv("CHRONOS_OPEN_BROWSER", default_open_browser).lower() == "true"
    url = f"http://{host}:{port}/"

    if open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    print(f"CHRONOS-SAFE web UI: {url}")
    uvicorn.run("chronos_safe.apps.api.main:app", host=host, port=port, reload=False)
>>>>>>> 3714e51ee15899694ba515e443224b640b045c7d


if __name__ == "__main__":
    main()
