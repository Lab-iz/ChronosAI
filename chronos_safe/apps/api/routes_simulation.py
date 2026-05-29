"""Simulation routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from chronos_safe.apps.api.schemas import SimulateRequest
from chronos_safe.domain.results import SimulationResult
from chronos_safe.simulation.mission_apophis import ApophisValidationConfig, run_apophis_validation
from chronos_safe.services.simulation import SimulationConfig, run_fixture_rollout, trajectory_payload

router = APIRouter(tags=["simulation"])


def _simulation_config(request: SimulateRequest) -> SimulationConfig:
    return SimulationConfig(
        fixture_name=request.fixture_name,
        steps=request.steps,
        dt_days=request.dt_days,
        checkpoint_path=request.checkpoint_path,
        scaler_path=request.scaler_path,
        ood_guard_path=request.ood_guard_path,
    )


def _run_rollout_or_raise(config: SimulationConfig) -> SimulationResult:
    try:
        return run_fixture_rollout(config)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Fixture not found: {config.fixture_name}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/simulate")
def simulate(request: SimulateRequest) -> dict[str, object]:
    result = _run_rollout_or_raise(_simulation_config(request))
    return result.to_dict()


@router.post("/simulate/trajectory")
def simulate_trajectory(request: SimulateRequest) -> dict[str, object]:
    result = _run_rollout_or_raise(_simulation_config(request))
    return trajectory_payload(result, dt_days=request.dt_days, source=request.fixture_name)


@router.post("/validate/apophis")
def validate_apophis(request: SimulateRequest) -> dict[str, object]:
    try:
        return run_apophis_validation(
            ApophisValidationConfig(
                steps=request.steps,
                dt_days=request.dt_days,
                fixture_name=request.fixture_name,
                checkpoint_path=None if request.checkpoint_path is None else Path(request.checkpoint_path),
                scaler_path=None if request.scaler_path is None else Path(request.scaler_path),
                ood_guard_path=None if request.ood_guard_path is None else Path(request.ood_guard_path),
            )
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Fixture not found: {request.fixture_name}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
