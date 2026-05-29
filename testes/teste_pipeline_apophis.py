from pathlib import Path

from chronos_seguro.simulacao.missao_apophis import ConfiguracaoValidacaoApophis, executar_validacao_apophis


def test_pipeline_apophis_gera_relatorio(tmp_path: Path) -> None:
    report_dir = tmp_path / "relatorios"
    report = executar_validacao_apophis(ConfiguracaoValidacaoApophis(steps=5, dt_days=1.0, report_dir=report_dir))
    assert "comparison_metrics" in report
    assert "benchmark" in report
    assert (report_dir / "validacao_apophis.json").exists()
    assert (report_dir / "resumo_validacao_apophis.txt").exists()
