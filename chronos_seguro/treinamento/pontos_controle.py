"""Utilitarios para pontos de controle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from chronos_seguro.utilitarios.serializacao import write_json

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None


def save_model_checkpoint(
    path: str | Path,
    model: object,
    optimizer: object | None,
    epoch: int,
    metrics: dict[str, Any],
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if torch is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch e necessario para salvar pontos de controle do modelo.")
    torch.save(
        {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": None if optimizer is None else optimizer.state_dict(),
            "metrics": metrics,
        },
        target,
    )


def load_model_checkpoint(path: str | Path, model: object, optimizer: object | None = None) -> dict[str, Any]:
    if torch is None:  # pragma: no cover - exercised only without torch
        raise RuntimeError("PyTorch e necessario para carregar pontos de controle do modelo.")
    payload = torch.load(Path(path), map_location="cpu")
    model.load_state_dict(payload["model_state_dict"])
    if optimizer is not None and payload["optimizer_state_dict"] is not None:
        optimizer.load_state_dict(payload["optimizer_state_dict"])
    return payload


def save_training_manifest(path: str | Path, payload: dict[str, Any]) -> None:
    write_json(path, payload)
