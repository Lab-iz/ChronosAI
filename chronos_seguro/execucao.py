"""Preparacao de execucao compartilhada por inicializadores e processos de API publicados."""

from __future__ import annotations

import os
import threading
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from chronos_seguro.configuracao.ajustes import SETTINGS, Settings
from chronos_seguro.utilitarios.logs import configure_logging

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
        settings.data_root / "brutos",
        settings.data_root / "processados",
        settings.data_root / "cache",
        settings.data_root / "cenarios",
        settings.models_root,
        settings.models_root / "pontos_controle",
        settings.models_root / "escalonadores",
        settings.reports_root,
        settings.reports_root / "figuras",
        settings.reports_root / "comparativos",
        settings.reports_root / "validacao",
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


def run_web_server(app_path: str = "chronos_seguro.aplicativos.api.principal:app") -> None:
    try:
        import uvicorn
    except ImportError as exc:  # pragma: no cover - runtime dependency error
        raise RuntimeError(
            "uvicorn e necessario para rodar a interface web. Instale com: python -m pip install -e ."
        ) from exc

    configure_logging(SETTINGS.log_level)
    ensure_runtime_directories()
    config = web_server_config_from_env()

    if config.open_browser:
        threading.Timer(1.2, lambda: webbrowser.open(config.url)).start()

    print(f"Interface web CHRONOS-SEGURO: {config.url}")
    uvicorn.run(app_path, host=config.host, port=config.port, reload=False)
