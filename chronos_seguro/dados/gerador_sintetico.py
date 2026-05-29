"""Geracao sintetica de dados generalistas."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from chronos_seguro.configuracao.constantes import DEFAULT_MAX_BODIES
from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.dados.cache import save_manifest, save_npz_bundle
from chronos_seguro.dados.preprocessamento import construir_amostra_processada
from chronos_seguro.dados.escalonadores import PhysicalScaler
from chronos_seguro.dominio.estado import BodyState, SystemState
from chronos_seguro.fisica.referenciais import standardize_state
from chronos_seguro.fisica.integrador_rapido import QuickIntegrator
from chronos_seguro.fisica.motor_rebound import ReboundReferenceEngine
from chronos_seguro.utilitarios.semente import set_seed


@dataclass(slots=True)
class ConfiguracaoGeracaoSintetica:
    output_dir: Path
    num_samples: int = 128
    min_bodies: int = 2
    max_bodies: int = 6
    dt_days: float = 1.0
    seed: int = SETTINGS.seed
    max_padded_bodies: int = DEFAULT_MAX_BODIES


def _amostrar_orbita(
    rng: np.random.Generator,
    central_mass: float,
    semi_major_axis: float,
    eccentricity: float,
    inclination: float,
    phase: float,
) -> tuple[np.ndarray, np.ndarray]:
    radius = semi_major_axis * (1.0 - eccentricity**2) / (1.0 + eccentricity * np.cos(phase))
    position_plane = np.array([radius * np.cos(phase), radius * np.sin(phase), 0.0], dtype=np.float64)
    speed = np.sqrt(2.9591220828559093e-4 * central_mass * (2.0 / radius - 1.0 / semi_major_axis))
    velocity_plane = np.array([-speed * np.sin(phase), speed * np.cos(phase), 0.0], dtype=np.float64)
    rot_x = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, np.cos(inclination), -np.sin(inclination)],
            [0.0, np.sin(inclination), np.cos(inclination)],
        ],
        dtype=np.float64,
    )
    return rot_x @ position_plane, rot_x @ velocity_plane


def sistema_orbital_aleatorio(rng: np.random.Generator, num_bodies: int) -> SystemState:
    central_mass = 1.0
    bodies = [BodyState("sun", central_mass, np.zeros(3), np.zeros(3))]
    for index in range(1, num_bodies):
        semi_major_axis = rng.uniform(0.4, 3.5)
        eccentricity = rng.uniform(0.0, 0.2)
        inclination = rng.uniform(0.0, 0.15)
        phase = rng.uniform(0.0, 2.0 * np.pi)
        mass = 10 ** rng.uniform(-10, -5)
        position, velocity = _amostrar_orbita(rng, central_mass, semi_major_axis, eccentricity, inclination, phase)
        bodies.append(BodyState(f"body_{index:02d}", mass, position, velocity))
    return standardize_state(SystemState.from_bodies(bodies, metadata={"source": "synthetic"}))


def gerar_dataset_generalista(config: ConfiguracaoGeracaoSintetica) -> Path:
    set_seed(config.seed)
    rng = np.random.default_rng(config.seed)
    quick = QuickIntegrator(dt_days=config.dt_days)
    reference = ReboundReferenceEngine(dt_days=config.dt_days, use_rebound=SETTINGS.use_rebound_if_available)
    samples = []
    for _ in range(config.num_samples):
        num_bodies = int(rng.integers(config.min_bodies, config.max_bodies + 1))
        initial_state = sistema_orbital_aleatorio(rng, num_bodies)
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
    ids = samples[0].ids if samples else []
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
            "kind": "generalista",
            "num_samples": config.num_samples,
            "dt_days": config.dt_days,
            "body_ids_template": ids,
            "max_padded_bodies": config.max_padded_bodies,
            "seed": config.seed,
        },
    )
    return config.output_dir


SyntheticGenerationConfig = ConfiguracaoGeracaoSintetica
random_orbital_system = sistema_orbital_aleatorio
generate_generalista_dataset = gerar_dataset_generalista
