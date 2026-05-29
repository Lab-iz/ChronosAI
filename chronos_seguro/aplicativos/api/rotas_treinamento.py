"""Rotas de treinamento."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from chronos_seguro.aplicativos.api.esquemas import RequisicaoTreinamento

router = APIRouter(prefix="/treinar", tags=["treinamento"])


@router.post("/generalista")
def treinar_generalista(request: RequisicaoTreinamento) -> dict[str, object]:
    try:
        from chronos_seguro.treinamento.treinar_generalista import executar_treino_generalista

        return executar_treino_generalista(
            dataset_dir=request.dataset_dir,
            output_dir=request.output_dir,
            epochs=request.epochs,
            batch_size=request.batch_size,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/especialista")
def treinar_especialista(request: RequisicaoTreinamento) -> dict[str, object]:
    try:
        from chronos_seguro.treinamento.treinar_especialista import executar_treino_especialista

        return executar_treino_especialista(
            dataset_dir=request.dataset_dir,
            output_dir=request.output_dir,
            base_checkpoint=request.base_checkpoint,
            epochs=request.epochs,
            batch_size=request.batch_size,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
