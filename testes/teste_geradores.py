from pathlib import Path

from chronos_seguro.dados.gerador_especialista import ConfiguracaoGeracaoEspecialista, gerar_dataset_especialista
from chronos_seguro.dados.gerador_sintetico import ConfiguracaoGeracaoSintetica, gerar_dataset_generalista


def test_gerador_generalista_persiste_dataset(tmp_path: Path) -> None:
    output_dir = tmp_path / "generalista"
    gerar_dataset_generalista(ConfiguracaoGeracaoSintetica(output_dir=output_dir, num_samples=8, min_bodies=2, max_bodies=3))
    assert (output_dir / "dataset.npz").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "scaler.json").exists()


def test_gerador_especialista_persiste_dataset(tmp_path: Path) -> None:
    output_dir = tmp_path / "especialista"
    gerar_dataset_especialista(ConfiguracaoGeracaoEspecialista(output_dir=output_dir, num_samples=6))
    assert (output_dir / "dataset.npz").exists()
    assert (output_dir / "manifest.json").exists()
    assert (output_dir / "scaler.json").exists()
