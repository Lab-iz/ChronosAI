"""Entrada de treinamento generalista."""

from __future__ import annotations

from pathlib import Path

from chronos_seguro.treinamento.treinador import ConfiguracaoTreinamento, treinar_modelo


def executar_treino_generalista(
    dataset_dir: str | Path,
    output_dir: str | Path,
    epochs: int = 20,
    batch_size: int = 16,
    learning_rate: float = 1.0e-3,
) -> dict[str, object]:
    return treinar_modelo(
        ConfiguracaoTreinamento(
            dataset_dir=Path(dataset_dir),
            output_dir=Path(output_dir),
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
        )
    )


run_train_generalista = executar_treino_generalista
