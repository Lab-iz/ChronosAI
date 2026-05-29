"""Utilitarios de graficos e resumo de relatorio."""

from __future__ import annotations

from pathlib import Path


def write_validacao_summary(path: str | Path, report: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "Resumo de Validacao Apophis - CHRONOS-SEGURO",
        f"Cenario: {report['fixture_name']}",
        f"Passos: {report['steps']}",
        f"dt_dias: {report['dt_days']}",
        f"Total de fallbacks: {report['fallback_count']}",
        f"Metricas de comparacao: {report['comparison_metrics']}",
        f"Metricas hibridas: {report['hybrid_metrics']}",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")
