"""Interface de linha de comando."""

from __future__ import annotations

import argparse
from pathlib import Path

from chronos_seguro.configuracao.ajustes import SETTINGS
from chronos_seguro.dados.gerador_especialista import ConfiguracaoGeracaoEspecialista, gerar_dataset_especialista
from chronos_seguro.dados.gerador_sintetico import ConfiguracaoGeracaoSintetica, gerar_dataset_generalista
from chronos_seguro.execucao import ensure_runtime_directories
from chronos_seguro.servicos.simulacao import ConfiguracaoSimulacao, executar_propagacao_cenario
from chronos_seguro.simulacao.missao_apophis import ConfiguracaoValidacaoApophis, executar_validacao_apophis
from chronos_seguro.treinamento.treinar_generalista import executar_treino_generalista
from chronos_seguro.treinamento.treinar_especialista import executar_treino_especialista
from chronos_seguro.utilitarios.serializacao import write_json


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chronos", description="Interface de linha de comando do CHRONOS-SEGURO")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_generalista = subparsers.add_parser("gerar-generalista")
    gen_generalista.add_argument("--diretorio-saida", "--output-dir", dest="output_dir", default=str(SETTINGS.data_root / "processados" / "generalista"))
    gen_generalista.add_argument("--num-amostras", "--num-samples", dest="num_samples", type=int, default=128)
    gen_generalista.add_argument("--min-corpos", "--min-bodies", dest="min_bodies", type=int, default=2)
    gen_generalista.add_argument("--max-corpos", "--max-bodies", dest="max_bodies", type=int, default=6)
    gen_generalista.add_argument("--dt-dias", "--dt-days", dest="dt_days", type=float, default=1.0)

    gen_especialista = subparsers.add_parser("gerar-especialista")
    gen_especialista.add_argument("--diretorio-saida", "--output-dir", dest="output_dir", default=str(SETTINGS.data_root / "processados" / "especialista"))
    gen_especialista.add_argument("--cenario", "--fixture-name", dest="fixture_name", default="apophis/cenario_apophis.json")
    gen_especialista.add_argument("--num-amostras", "--num-samples", dest="num_samples", type=int, default=64)
    gen_especialista.add_argument("--dt-dias", "--dt-days", dest="dt_days", type=float, default=1.0)

    train_generalista = subparsers.add_parser("treinar-generalista")
    train_generalista.add_argument("--diretorio-dataset", "--dataset-dir", dest="dataset_dir", default=str(SETTINGS.data_root / "processados" / "generalista"))
    train_generalista.add_argument("--diretorio-saida", "--output-dir", dest="output_dir", default=str(SETTINGS.models_root / "pontos_controle" / "generalista"))
    train_generalista.add_argument("--epocas", "--epochs", dest="epochs", type=int, default=20)
    train_generalista.add_argument("--tamanho-lote", "--batch-size", dest="batch_size", type=int, default=16)

    train_especialista = subparsers.add_parser("treinar-especialista")
    train_especialista.add_argument("--diretorio-dataset", "--dataset-dir", dest="dataset_dir", default=str(SETTINGS.data_root / "processados" / "especialista"))
    train_especialista.add_argument("--diretorio-saida", "--output-dir", dest="output_dir", default=str(SETTINGS.models_root / "pontos_controle" / "especialista"))
    train_especialista.add_argument("--ponto-controle-base", "--base-checkpoint", dest="base_checkpoint", default=None)
    train_especialista.add_argument("--epocas", "--epochs", dest="epochs", type=int, default=10)
    train_especialista.add_argument("--tamanho-lote", "--batch-size", dest="batch_size", type=int, default=16)

    simular_parser = subparsers.add_parser("simular")
    simular_parser.add_argument("--cenario", "--fixture-name", dest="fixture_name", default="apophis/cenario_apophis.json")
    simular_parser.add_argument("--passos", "--steps", dest="steps", type=int, default=30)
    simular_parser.add_argument("--dt-dias", "--dt-days", dest="dt_days", type=float, default=1.0)
    simular_parser.add_argument("--ponto-controle", "--checkpoint-path", dest="checkpoint_path", default=None)
    simular_parser.add_argument("--escalonador", "--scaler-path", dest="scaler_path", default=None)
    simular_parser.add_argument("--guarda-ood", "--ood-guard-path", dest="ood_guard_path", default=None)
    simular_parser.add_argument(
        "--saida",
        "--output-path",
        dest="output_path",
        default=str(SETTINGS.reports_root / "validacao" / "simulacao.json"),
    )

    apophis = subparsers.add_parser("validar-apophis")
    apophis.add_argument("--passos", "--steps", dest="steps", type=int, default=180)
    apophis.add_argument("--dt-dias", "--dt-days", dest="dt_days", type=float, default=1.0)
    apophis.add_argument("--ponto-controle", "--checkpoint-path", dest="checkpoint_path", default=None)
    apophis.add_argument("--escalonador", "--scaler-path", dest="scaler_path", default=None)
    apophis.add_argument("--guarda-ood", "--ood-guard-path", dest="ood_guard_path", default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    ensure_runtime_directories()
    if args.command == "gerar-generalista":
        gerar_dataset_generalista(
            ConfiguracaoGeracaoSintetica(
                output_dir=Path(args.output_dir),
                num_samples=args.num_samples,
                min_bodies=args.min_bodies,
                max_bodies=args.max_bodies,
                dt_days=args.dt_days,
            )
        )
        return
    if args.command == "gerar-especialista":
        gerar_dataset_especialista(
            ConfiguracaoGeracaoEspecialista(
                output_dir=Path(args.output_dir),
                fixture_name=args.fixture_name,
                num_samples=args.num_samples,
                dt_days=args.dt_days,
            )
        )
        return
    if args.command == "treinar-generalista":
        executar_treino_generalista(args.dataset_dir, args.output_dir, epochs=args.epochs, batch_size=args.batch_size)
        return
    if args.command == "treinar-especialista":
        executar_treino_especialista(
            args.dataset_dir,
            args.output_dir,
            base_checkpoint=args.base_checkpoint,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
        return
    if args.command == "simular":
        result = executar_propagacao_cenario(
            ConfiguracaoSimulacao(
                fixture_name=args.fixture_name,
                steps=args.steps,
                dt_days=args.dt_days,
                checkpoint_path=args.checkpoint_path,
                scaler_path=args.scaler_path,
                ood_guard_path=args.ood_guard_path,
            )
        )
        write_json(args.output_path, result.to_dict())
        return
    if args.command == "validar-apophis":
        executar_validacao_apophis(
            ConfiguracaoValidacaoApophis(
                steps=args.steps,
                dt_days=args.dt_days,
                checkpoint_path=None if args.checkpoint_path is None else Path(args.checkpoint_path),
                scaler_path=None if args.scaler_path is None else Path(args.scaler_path),
                ood_guard_path=None if args.ood_guard_path is None else Path(args.ood_guard_path),
            )
        )
        return


if __name__ == "__main__":
    main()
