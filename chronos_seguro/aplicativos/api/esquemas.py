"""Esquemas da API."""

from __future__ import annotations

from typing import Self

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class EsquemaAPI(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class RequisicaoTreinamento(EsquemaAPI):
    dataset_dir: str = Field(min_length=1, validation_alias=AliasChoices("dataset_dir", "diretorio_dataset"))
    output_dir: str = Field(min_length=1, validation_alias=AliasChoices("output_dir", "diretorio_saida"))
    base_checkpoint: str | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("base_checkpoint", "ponto_controle_base"),
    )
    epochs: int = Field(default=20, ge=1, validation_alias=AliasChoices("epochs", "epocas"))
    batch_size: int = Field(default=16, ge=1, validation_alias=AliasChoices("batch_size", "tamanho_lote"))


class RequisicaoGerarGeneralista(EsquemaAPI):
    output_dir: str = Field(min_length=1, validation_alias=AliasChoices("output_dir", "diretorio_saida"))
    num_samples: int = Field(default=128, ge=1, validation_alias=AliasChoices("num_samples", "num_amostras"))
    min_bodies: int = Field(default=2, ge=2, validation_alias=AliasChoices("min_bodies", "min_corpos"))
    max_bodies: int = Field(default=6, ge=2, validation_alias=AliasChoices("max_bodies", "max_corpos"))
    dt_days: float = Field(default=1.0, gt=0.0, validation_alias=AliasChoices("dt_days", "dt_dias"))

    @model_validator(mode="after")
    def validar_intervalo_corpos(self) -> Self:
        if self.max_bodies < self.min_bodies:
            raise ValueError("max_corpos deve ser maior ou igual a min_corpos")
        return self


class RequisicaoGerarEspecialista(EsquemaAPI):
    output_dir: str = Field(min_length=1, validation_alias=AliasChoices("output_dir", "diretorio_saida"))
    fixture_name: str = Field(
        default="apophis/cenario_apophis.json",
        min_length=1,
        validation_alias=AliasChoices("fixture_name", "cenario"),
    )
    num_samples: int = Field(default=64, ge=1, validation_alias=AliasChoices("num_samples", "num_amostras"))
    dt_days: float = Field(default=1.0, gt=0.0, validation_alias=AliasChoices("dt_days", "dt_dias"))


class RequisicaoSimulacao(EsquemaAPI):
    fixture_name: str = Field(
        default="apophis/cenario_apophis.json",
        min_length=1,
        validation_alias=AliasChoices("fixture_name", "cenario"),
    )
    steps: int = Field(default=30, ge=1, validation_alias=AliasChoices("steps", "passos"))
    dt_days: float = Field(default=1.0, gt=0.0, validation_alias=AliasChoices("dt_days", "dt_dias"))
    checkpoint_path: str | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("checkpoint_path", "ponto_controle"),
    )
    scaler_path: str | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("scaler_path", "escalonador"),
    )
    ood_guard_path: str | None = Field(
        default=None,
        min_length=1,
        validation_alias=AliasChoices("ood_guard_path", "guarda_ood"),
    )


class RespostaSaude(EsquemaAPI):
    status: str
    version: str = Field(validation_alias=AliasChoices("version", "versao"))


TrainRequest = RequisicaoTreinamento
GenerateGeneralistaRequest = RequisicaoGerarGeneralista
GenerateEspecialistaRequest = RequisicaoGerarEspecialista
SimulateRequest = RequisicaoSimulacao
HealthResponse = RespostaSaude
