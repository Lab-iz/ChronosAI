"""Servicos compartilhados de orquestracao de simulacao."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.dados.cliente_horizons import HorizonsClient
from chronos_seguro.dados.escalonadores import PhysicalScaler
from chronos_seguro.dominio.resultados import SimulationResult
from chronos_seguro.dominio.estado import SystemState
from chronos_seguro.modelos.guarda_ood import OODGuard
from chronos_seguro.fisica.integrador_rapido import QuickIntegrator
from chronos_seguro.fisica.motor_rebound import ReboundReferenceEngine
from chronos_seguro.simulacao.motor_hibrido import HybridEngine, load_torch_model
from chronos_seguro.simulacao.propagacao import RolloutConfig, run_hybrid_rollout
from chronos_seguro.utilitarios.dispositivo import get_device


@dataclass(frozen=True, slots=True)
class ConfiguracaoSimulacao:
    fixture_name: str = "apophis/cenario_apophis.json"
    steps: int = 30
    dt_days: float = 1.0
    checkpoint_path: str | Path | None = None
    scaler_path: str | Path | None = None
    ood_guard_path: str | Path | None = None


def carregar_estado_cenario(fixture_name: str, client: HorizonsClient | None = None) -> SystemState:
    horizons_client = client or HorizonsClient()
    return horizons_client.load_fixture(fixture_name)


def construir_motor_hibrido(
    *,
    dt_days: float,
    checkpoint_path: str | Path | None = None,
    scaler_path: str | Path | None = None,
    ood_guard_path: str | Path | None = None,
    use_rebound: bool | None = None,
) -> HybridEngine:
    device = get_device(SETTINGS.device)
    model = load_torch_model(checkpoint_path, device=device) if checkpoint_path else None
    scaler = PhysicalScaler.load(scaler_path) if scaler_path else None
    ood_guard = OODGuard.load(ood_guard_path) if ood_guard_path else None
    return HybridEngine(
        quick_integrator=QuickIntegrator(dt_days=dt_days),
        reference_engine=ReboundReferenceEngine(
            dt_days=dt_days,
            use_rebound=SETTINGS.use_rebound_if_available if use_rebound is None else use_rebound,
        ),
        model=model,
        scaler=scaler,
        ood_guard=ood_guard,
        device=device,
    )


def executar_propagacao_cenario(config: ConfiguracaoSimulacao) -> SimulationResult:
    initial_state = carregar_estado_cenario(config.fixture_name)
    engine = construir_motor_hibrido(
        dt_days=config.dt_days,
        checkpoint_path=config.checkpoint_path,
        scaler_path=config.scaler_path,
        ood_guard_path=config.ood_guard_path,
    )
    return run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=config.steps, dt_days=config.dt_days))


def montar_payload_trajetoria(result: SimulationResult, *, dt_days: float, source: str) -> dict[str, object]:
    return {
        "source": source,
        "ids": list(result.states[0].ids),
        "frames": [state.positions.tolist() for state in result.states],
        "dt_days": dt_days,
        "metrics": dict(result.metrics),
        "fallback_events": [event.to_dict() for event in result.fallback_events],
    }


SimulationConfig = ConfiguracaoSimulacao
load_fixture_state = carregar_estado_cenario
build_hybrid_engine = construir_motor_hibrido
run_fixture_rollout = executar_propagacao_cenario
trajectory_payload = montar_payload_trajetoria
