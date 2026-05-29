"""Rotas de geracao de dados."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException

from chronos_seguro.aplicativos.api.esquemas import RequisicaoGerarEspecialista, RequisicaoGerarGeneralista
from chronos_seguro.dados.gerador_especialista import ConfiguracaoGeracaoEspecialista, gerar_dataset_especialista
from chronos_seguro.dados.gerador_sintetico import ConfiguracaoGeracaoSintetica, gerar_dataset_generalista

router = APIRouter(prefix="/gerar", tags=["dados"])


@router.post("/generalista")
def gerar_generalista(request: RequisicaoGerarGeneralista) -> dict[str, object]:
    output_dir = gerar_dataset_generalista(
        ConfiguracaoGeracaoSintetica(
            output_dir=Path(request.output_dir),
            num_samples=request.num_samples,
            min_bodies=request.min_bodies,
            max_bodies=request.max_bodies,
            dt_days=request.dt_days,
        )
    )
    return {"status": "ok", "kind": "generalista", "output_dir": str(output_dir.as_posix())}


@router.post("/especialista")
def gerar_especialista(request: RequisicaoGerarEspecialista) -> dict[str, object]:
    try:
        output_dir = gerar_dataset_especialista(
            ConfiguracaoGeracaoEspecialista(
                output_dir=Path(request.output_dir),
                fixture_name=request.fixture_name,
                num_samples=request.num_samples,
                dt_days=request.dt_days,
            )
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Cenario nao encontrado: {request.fixture_name}") from exc
    return {"status": "ok", "kind": "especialista", "output_dir": str(output_dir.as_posix())}
