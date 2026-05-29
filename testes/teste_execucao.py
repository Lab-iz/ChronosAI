from pathlib import Path

from chronos_safe.config.settings import SETTINGS
from chronos_safe.runtime import runtime_directories, web_server_config_from_env


def test_web_server_config_defaults_to_local_browser() -> None:
    config = web_server_config_from_env({})
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.open_browser


def test_web_server_config_disables_browser_on_render_port() -> None:
    config = web_server_config_from_env({"PORT": "10000"})
    assert config.host == "0.0.0.0"
    assert config.port == 10000
    assert not config.open_browser


def test_runtime_directories_are_under_project_roots() -> None:
    directories = runtime_directories()
    assert SETTINGS.data_root in directories
    assert SETTINGS.models_root in directories
    assert SETTINGS.reports_root in directories
    assert all(isinstance(path, Path) for path in directories)
