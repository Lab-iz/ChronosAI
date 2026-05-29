"""Rotas de simulacao."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from chronos_seguro.aplicativos.api.esquemas import RequisicaoSimulacao
from chronos_seguro.dominio.resultados import SimulationResult
from chronos_seguro.simulacao.missao_apophis import ConfiguracaoValidacaoApophis, executar_validacao_apophis
from chronos_seguro.servicos.simulacao import (
    ConfiguracaoSimulacao,
    executar_propagacao_cenario,
    montar_payload_trajetoria,
)

router = APIRouter(tags=["simulacao"])


def _configuracao_simulacao(request: RequisicaoSimulacao) -> ConfiguracaoSimulacao:
    return ConfiguracaoSimulacao(
        fixture_name=request.fixture_name,
        steps=request.steps,
        dt_days=request.dt_days,
        checkpoint_path=request.checkpoint_path,
        scaler_path=request.scaler_path,
        ood_guard_path=request.ood_guard_path,
    )


def _executar_propagacao_ou_erro(config: ConfiguracaoSimulacao) -> SimulationResult:
    try:
        return executar_propagacao_cenario(config)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Cenario nao encontrado: {config.fixture_name}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/simular")
def simular(request: RequisicaoSimulacao) -> dict[str, object]:
    result = _executar_propagacao_ou_erro(_configuracao_simulacao(request))
    return result.to_dict()


@router.post("/simular/trajetoria")
def simular_trajetoria(request: RequisicaoSimulacao) -> dict[str, object]:
    result = _executar_propagacao_ou_erro(_configuracao_simulacao(request))
    return montar_payload_trajetoria(result, dt_days=request.dt_days, source=request.fixture_name)


@router.post("/validar/apophis")
def validar_apophis(request: RequisicaoSimulacao) -> dict[str, object]:
    try:
        return executar_validacao_apophis(
            ConfiguracaoValidacaoApophis(
                steps=request.steps,
                dt_days=request.dt_days,
                fixture_name=request.fixture_name,
                checkpoint_path=None if request.checkpoint_path is None else Path(request.checkpoint_path),
                scaler_path=None if request.scaler_path is None else Path(request.scaler_path),
                ood_guard_path=None if request.ood_guard_path is None else Path(request.ood_guard_path),
            )
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Cenario nao encontrado: {request.fixture_name}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
