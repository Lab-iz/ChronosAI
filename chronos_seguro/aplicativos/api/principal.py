"""Aplicacao FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from chronos_seguro.aplicativos.api.rotas_dados import router as roteador_dados
from chronos_seguro.aplicativos.api.rotas_simulacao import router as roteador_simulacao
from chronos_seguro.aplicativos.api.rotas_treinamento import router as roteador_treinamento
from chronos_seguro.aplicativos.api.esquemas import RespostaSaude
from chronos_seguro.aplicativos.api.interface_web import montar_payload_catalogo, renderizar_html_painel
from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.execucao import ensure_runtime_directories
from chronos_seguro.utilitarios.logs import configure_logging
from chronos_seguro.versao import __version__

STATIC_DIR = Path(__file__).with_name("static")


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(SETTINGS.log_level)
    ensure_runtime_directories()
    yield


def criar_app() -> FastAPI:
    app = FastAPI(
        title="CHRONOS-SEGURO",
        version=__version__,
        description=(
            "Plataforma educacional para aprender a passagem segura de Apophis em 2029 "
            "e visualizar simulacoes de muitos corpos em 3D."
        ),
        lifespan=lifespan,
    )
    app.include_router(roteador_dados)
    app.include_router(roteador_treinamento)
    app.include_router(roteador_simulacao)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = criar_app()


@app.get("/", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    return HTMLResponse(renderizar_html_painel())


@app.get("/health", response_model=RespostaSaude)
def saude() -> RespostaSaude:
    return RespostaSaude(status="ok", version=__version__)


@app.get("/ui/catalog")
def catalogo_ui() -> dict[str, object]:
    return montar_payload_catalogo()


create_app = criar_app
HealthResponse = RespostaSaude
