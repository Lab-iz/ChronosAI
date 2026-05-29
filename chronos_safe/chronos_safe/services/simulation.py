"""Shared simulation orchestration services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chronos_safe.config.settings import SETTINGS
from chronos_safe.data.horizons_client import HorizonsClient
from chronos_safe.data.scalers import PhysicalScaler
from chronos_safe.domain.results import SimulationResult
from chronos_safe.domain.state import SystemState
from chronos_safe.models.ood_guard import OODGuard
from chronos_safe.physics.quick_integrator import QuickIntegrator
from chronos_safe.physics.rebound_engine import ReboundReferenceEngine
from chronos_safe.simulation.hybrid_engine import HybridEngine, load_torch_model
from chronos_safe.simulation.rollout import RolloutConfig, run_hybrid_rollout
from chronos_safe.utils.device import get_device


@dataclass(frozen=True, slots=True)
class SimulationConfig:
    fixture_name: str = "apophis/apophis_fixture.json"
    steps: int = 30
    dt_days: float = 1.0
    checkpoint_path: str | Path | None = None
    scaler_path: str | Path | None = None
    ood_guard_path: str | Path | None = None


def load_fixture_state(fixture_name: str, client: HorizonsClient | None = None) -> SystemState:
    horizons_client = client or HorizonsClient()
    return horizons_client.load_fixture(fixture_name)


def build_hybrid_engine(
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


def run_fixture_rollout(config: SimulationConfig) -> SimulationResult:
    initial_state = load_fixture_state(config.fixture_name)
    engine = build_hybrid_engine(
        dt_days=config.dt_days,
        checkpoint_path=config.checkpoint_path,
        scaler_path=config.scaler_path,
        ood_guard_path=config.ood_guard_path,
    )
    return run_hybrid_rollout(initial_state, engine, RolloutConfig(steps=config.steps, dt_days=config.dt_days))


def trajectory_payload(result: SimulationResult, *, dt_days: float, source: str) -> dict[str, object]:
    return {
        "source": source,
        "ids": list(result.states[0].ids),
        "frames": [state.positions.tolist() for state in result.states],
        "dt_days": dt_days,
        "metrics": dict(result.metrics),
        "fallback_events": [event.to_dict() for event in result.fallback_events],
    }
