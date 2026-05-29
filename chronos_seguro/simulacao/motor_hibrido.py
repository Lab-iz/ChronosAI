"""Motor de simulacao hibrida."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chronos_seguro.dados.escalonadores import PhysicalScaler
from chronos_seguro.dominio.resultados import FallbackEvent
from chronos_seguro.dominio.estado import SystemState
from chronos_seguro.modelos.guarda_ood import OODGuard
from chronos_seguro.fisica.integrador_rapido import QuickIntegrator
from chronos_seguro.fisica.motor_rebound import ReboundReferenceEngine
from chronos_seguro.simulacao.chave_segura import evaluate_state_safety
from chronos_seguro.utilitarios.dispositivo import get_device

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None


def _to_numpy(value: object) -> np.ndarray:
    if torch is not None and isinstance(value, torch.Tensor):
        return value.detach().cpu().numpy()
    return np.asarray(value, dtype=np.float64)


@dataclass(slots=True)
class HybridStepOutput:
    state: SystemState
    fallback_event: FallbackEvent | None
    used_fallback: bool
    ood_score: float


@dataclass(slots=True)
class HybridEngine:
    quick_integrator: QuickIntegrator
    reference_engine: ReboundReferenceEngine
    model: object | None = None
    scaler: PhysicalScaler | None = None
    ood_guard: OODGuard | None = None
    device: str = "cpu"

    def _predict_residual(self, state: SystemState) -> tuple[np.ndarray, float]:
        masses = state.masses[None, ...]
        positions = state.positions[None, ...]
        velocities = state.velocities[None, ...]
        mask = np.ones((1, state.num_bodies), dtype=bool)
        ood_score = 0.0 if self.ood_guard is None else self.ood_guard.score_single(state.masses, state.positions, state.velocities, mask[0])
        if self.model is None or torch is None:
            return np.zeros_like(state.positions), ood_score

        if self.scaler is not None:
            batch = self.scaler.transform_batch(
                {
                    "masses": masses,
                    "positions": positions,
                    "velocities": velocities,
                    "target_delta_acc": np.zeros_like(positions),
                    "mask": mask,
                }
            )
            masses_in = torch.as_tensor(batch["masses_scaled"], dtype=torch.float32, device=self.device)
            positions_in = torch.as_tensor(batch["positions_scaled"], dtype=torch.float32, device=self.device)
            velocities_in = torch.as_tensor(batch["velocities_scaled"], dtype=torch.float32, device=self.device)
        else:
            masses_in = torch.as_tensor(masses, dtype=torch.float32, device=self.device)
            positions_in = torch.as_tensor(positions, dtype=torch.float32, device=self.device)
            velocities_in = torch.as_tensor(velocities, dtype=torch.float32, device=self.device)
        mask_in = torch.as_tensor(mask, dtype=torch.bool, device=self.device)
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(masses_in, positions_in, velocities_in, mask_in)
        residual = _to_numpy(prediction)[0]
        if self.scaler is not None:
            residual = self.scaler.inverse_target(residual)
        return residual, ood_score

    def _apply_residual(self, quick_state: SystemState, residual_acceleration: np.ndarray, dt_days: float) -> SystemState:
        corrected = quick_state.copy()
        corrected.positions = corrected.positions + 0.5 * residual_acceleration * dt_days**2
        corrected.velocities = corrected.velocities + residual_acceleration * dt_days
        corrected.metadata["integrator"] = "hybrid"
        return corrected

    def step(
        self,
        current_state: SystemState,
        step: int,
        time_days: float,
        baseline_energy: float | None = None,
        baseline_angular_momentum: np.ndarray | None = None,
    ) -> HybridStepOutput:
        quick_state = self.quick_integrator.step(current_state)
        residual_acceleration, ood_score = self._predict_residual(current_state)
        candidate_state = self._apply_residual(quick_state, residual_acceleration, self.quick_integrator.dt_days)
        decision, event = evaluate_state_safety(
            current_state=current_state,
            candidate_state=candidate_state,
            residual_acceleration=residual_acceleration,
            step=step,
            time_days=time_days,
            ood_score=ood_score,
            ood_threshold=None if self.ood_guard is None else self.ood_guard.threshold,
            baseline_energy=baseline_energy,
            baseline_angular_momentum=baseline_angular_momentum,
        )
        if decision.safe:
            return HybridStepOutput(candidate_state, None, False, ood_score)
        fallback_state = self.reference_engine.step(current_state)
        fallback_state.metadata["fallback_reason"] = decision.reason
        return HybridStepOutput(fallback_state, event, True, ood_score)


def load_torch_model(checkpoint_path: str | Path, device: str = "cpu") -> object:
    if torch is None:  # pragma: no cover
        raise RuntimeError("PyTorch e necessario para carregar um modelo treinado.")
    from chronos_seguro.modelos.gnn_residual import ResidualGNN, ResidualGNNConfig

    resolved_device = get_device(device)
    model = ResidualGNN(ResidualGNNConfig()).to(resolved_device)
    payload = torch.load(Path(checkpoint_path), map_location=resolved_device)
    if "model_state_dict" in payload:
        model.load_state_dict(payload["model_state_dict"])
    else:
        model.load_state_dict(payload)
    return model
