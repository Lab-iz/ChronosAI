from pathlib import Path

from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.execucao import runtime_directories, web_server_config_from_env


def test_config_servidor_web_abre_navegador_local_por_padrao() -> None:
    config = web_server_config_from_env({})
    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.open_browser


def test_config_servidor_web_desativa_navegador_com_porta_render() -> None:
    config = web_server_config_from_env({"PORT": "10000"})
    assert config.host == "0.0.0.0"
    assert config.port == 10000
    assert not config.open_browser


def test_diretorios_execucao_ficam_nas_raizes_do_projeto() -> None:
    directories = runtime_directories()
    assert SETTINGS.data_root in directories
    assert SETTINGS.models_root in directories
    assert SETTINGS.reports_root in directories
    assert all(isinstance(path, Path) for path in directories)
