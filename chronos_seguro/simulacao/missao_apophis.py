"""Pipeline offline de validacao Apophis."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.avaliacao.comparativo import benchmark_rollouts
from chronos_seguro.avaliacao.metricas import compare_rollouts
from chronos_seguro.avaliacao.graficos import write_validacao_summary
from chronos_seguro.servicos.simulacao import carregar_estado_cenario, construir_motor_hibrido
from chronos_seguro.simulacao.propagacao import RolloutConfig
from chronos_seguro.utilitarios.serializacao import write_json


@dataclass(slots=True)
class ConfiguracaoValidacaoApophis:
    steps: int = 180
    dt_days: float = 1.0
    fixture_name: str = "apophis/cenario_apophis.json"
    report_dir: Path = SETTINGS.reports_root / "validacao"
    checkpoint_path: Path | None = None
    scaler_path: Path | None = None
    ood_guard_path: Path | None = None


def executar_validacao_apophis(config: ConfiguracaoValidacaoApophis) -> dict[str, object]:
    initial_state = carregar_estado_cenario(config.fixture_name)
    hybrid_engine = construir_motor_hibrido(
        dt_days=config.dt_days,
        checkpoint_path=config.checkpoint_path,
        scaler_path=config.scaler_path,
        ood_guard_path=config.ood_guard_path,
    )
    rollout_config = RolloutConfig(steps=config.steps, dt_days=config.dt_days)

    benchmark = benchmark_rollouts(initial_state, hybrid_engine, hybrid_engine.reference_engine, rollout_config)
    hybrid_result = benchmark["hybrid"]
    comparison_metrics = compare_rollouts(benchmark["reference"].states, hybrid_result.states)

    report = {
        "fixture_name": config.fixture_name,
        "steps": config.steps,
        "dt_days": config.dt_days,
        "checkpoint_path": None if config.checkpoint_path is None else str(config.checkpoint_path),
        "scaler_path": None if config.scaler_path is None else str(config.scaler_path),
        "ood_guard_path": None if config.ood_guard_path is None else str(config.ood_guard_path),
        "ids": list(initial_state.ids),
        "reference_frames": [state.positions.tolist() for state in benchmark["reference"].states],
        "hybrid_frames": [state.positions.tolist() for state in hybrid_result.states],
        "hybrid_metrics": hybrid_result.metrics,
        "comparison_metrics": comparison_metrics,
        "fallback_count": len(hybrid_result.fallback_events),
        "fallback_events": [event.to_dict() for event in hybrid_result.fallback_events],
        "benchmark": {name: result.to_dict() for name, result in benchmark["benchmarks"].items()},
    }
    config.report_dir.mkdir(parents=True, exist_ok=True)
    write_json(config.report_dir / "validacao_apophis.json", report)
    write_validacao_summary(config.report_dir / "resumo_validacao_apophis.txt", report)
    return report


ApophisValidationConfig = ConfiguracaoValidacaoApophis
run_apophis_validacao = executar_validacao_apophis
