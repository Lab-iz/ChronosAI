"""Runtime setup shared by launchers and deployed API processes."""

from __future__ import annotations

import os
import threading
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from chronos_safe.config.settings import SETTINGS, Settings
from chronos_safe.utils.logging_utils import configure_logging

TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class WebServerConfig:
    host: str
    port: int
    open_browser: bool

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}/"


def runtime_directories(settings: Settings = SETTINGS) -> tuple[Path, ...]:
    return (
        settings.data_root,
        settings.data_root / "raw",
        settings.data_root / "processed",
        settings.data_root / "cache",
        settings.data_root / "fixtures",
        settings.models_root,
        settings.models_root / "checkpoints",
        settings.models_root / "scalers",
        settings.reports_root,
        settings.reports_root / "figures",
        settings.reports_root / "benchmarks",
        settings.reports_root / "validation",
    )


def ensure_runtime_directories(settings: Settings = SETTINGS) -> None:
    for path in runtime_directories(settings):
        path.mkdir(parents=True, exist_ok=True)


def web_server_config_from_env(env: Mapping[str, str] | None = None) -> WebServerConfig:
    values = os.environ if env is None else env
    render_port = values.get("PORT")
    host = values.get("CHRONOS_HOST", "0.0.0.0" if render_port else "127.0.0.1")
    port = int(render_port or values.get("CHRONOS_PORT", "8000"))
    default_open_browser = "false" if render_port else "true"
    open_browser = values.get("CHRONOS_OPEN_BROWSER", default_open_browser).strip().lower() in TRUE_VALUES
    return WebServerConfig(host=host, port=port, open_browser=open_browser)


def run_web_server(app_path: str = "chronos_safe.apps.api.main:app") -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - runtime dependency error
        raise RuntimeError(
            "uvicorn is required to run the web UI. Install with: python -m pip install -e ."
        ) from exc

    configure_logging(SETTINGS.log_level)
    ensure_runtime_directories()
    config = web_server_config_from_env()

    if config.open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(config.url)).start()

    print(f"CHRONOS-SAFE web UI: {config.url}")
    uvicorn.run(app_path, host=config.host, port=config.port, reload=False)
