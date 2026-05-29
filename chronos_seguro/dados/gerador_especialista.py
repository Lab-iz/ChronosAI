"""Geracao especialista de dados do Sistema Solar e de Apophis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chronos_seguro.configuracao.constantes import DEFAULT_MAX_BODIES
from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.dados.cache import save_manifest, save_npz_bundle
from chronos_seguro.dados.cliente_horizons import HorizonsClient
from chronos_seguro.dados.preprocessamento import construir_amostra_processada
from chronos_seguro.dados.escalonadores import PhysicalScaler
from chronos_seguro.dominio.estado import SystemState
from chronos_seguro.fisica.referenciais import standardize_state
from chronos_seguro.fisica.integrador_rapido import QuickIntegrator
from chronos_seguro.fisica.motor_rebound import ReboundReferenceEngine
from chronos_seguro.utilitarios.semente import set_seed


@dataclass(slots=True)
class ConfiguracaoGeracaoEspecialista:
    output_dir: Path
    fixture_name: str = "apophis/cenario_apophis.json"
    num_samples: int = 64
    dt_days: float = 1.0
    position_noise_std: float = 1.0e-4
    velocity_noise_std: float = 1.0e-5
    seed: int = SETTINGS.seed
    max_padded_bodies: int = DEFAULT_MAX_BODIES


def _perturbar_estado(
    rng: np.random.Generator,
    base_state: SystemState,
    position_noise_std: float,
    velocity_noise_std: float,
) -> SystemState:
    state = base_state.copy()
    state.positions = state.positions + rng.normal(0.0, position_noise_std, size=state.positions.shape)
    state.velocities = state.velocities + rng.normal(0.0, velocity_noise_std, size=state.velocities.shape)
    return standardize_state(state)


def gerar_dataset_especialista(config: ConfiguracaoGeracaoEspecialista) -> Path:
    set_seed(config.seed)
    rng = np.random.default_rng(config.seed)
    client = HorizonsClient()
    base_state = standardize_state(client.load_fixture(config.fixture_name))
    quick = QuickIntegrator(dt_days=config.dt_days)
    reference = ReboundReferenceEngine(dt_days=config.dt_days, use_rebound=SETTINGS.use_rebound_if_available)
    samples = []
    for _ in range(config.num_samples):
        initial_state = _perturbar_estado(rng, base_state, config.position_noise_std, config.velocity_noise_std)
        teacher_next = reference.step(initial_state)
        quick_next = quick.step(initial_state)
        samples.append(
            construir_amostra_processada(
                initial_state=initial_state,
                teacher_next=teacher_next,
                quick_next=quick_next,
                max_bodies=config.max_padded_bodies,
                dt_days=config.dt_days,
            )
        )
    arrays = {
        "masses": np.stack([sample.masses for sample in samples], axis=0),
        "positions": np.stack([sample.positions for sample in samples], axis=0),
        "velocities": np.stack([sample.velocities for sample in samples], axis=0),
        "target_delta_acc": np.stack([sample.target_delta_acc for sample in samples], axis=0),
        "teacher_positions_next": np.stack([sample.teacher_positions_next for sample in samples], axis=0),
        "teacher_velocities_next": np.stack([sample.teacher_velocities_next for sample in samples], axis=0),
        "mask": np.stack([sample.mask for sample in samples], axis=0),
    }
    config.output_dir.mkdir(parents=True, exist_ok=True)
    save_npz_bundle(config.output_dir / "dataset.npz", arrays)
    scaler = PhysicalScaler().fit(
        masses=arrays["masses"],
        positions=arrays["positions"],
        velocities=arrays["velocities"],
        targets=arrays["target_delta_acc"],
        mask=arrays["mask"],
    )
    scaler.save(str(config.output_dir / "scaler.json"))
    save_manifest(
        config.output_dir / "manifest.json",
        {
            "kind": "especialista",
            "fixture_name": config.fixture_name,
            "num_samples": config.num_samples,
            "dt_days": config.dt_days,
            "seed": config.seed,
            "max_padded_bodies": config.max_padded_bodies,
        },
    )
    return config.output_dir


EspecialistaGenerationConfig = ConfiguracaoGeracaoEspecialista
generate_especialista_dataset = gerar_dataset_especialista
