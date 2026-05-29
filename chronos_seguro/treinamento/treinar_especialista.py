"""Entrada de ajuste fino especialista."""

from __future__ import annotations

from pathlib import Path

from chronos_seguro.treinamento.treinador import ConfiguracaoTreinamento, treinar_modelo


def executar_treino_especialista(
    dataset_dir: str | Path,
    output_dir: str | Path,
    base_checkpoint: str | Path | None = None,
    epochs: int = 10,
    batch_size: int = 16,
    learning_rate: float = 5.0e-4,
) -> dict[str, object]:
    return treinar_modelo(
        ConfiguracaoTreinamento(
            dataset_dir=Path(dataset_dir),
            output_dir=Path(output_dir),
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            initial_checkpoint=None if base_checkpoint is None else Path(base_checkpoint),
        )
    )


run_train_especialista = executar_treino_especialista
