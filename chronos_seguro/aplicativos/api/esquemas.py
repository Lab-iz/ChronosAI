"""API schemas."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, Field, model_validator


class TrainRequest(BaseModel):
    dataset_dir: str = Field(min_length=1)
    output_dir: str = Field(min_length=1)
    base_checkpoint: str | None = Field(default=None, min_length=1)
    epochs: int = Field(default=20, ge=1)
    batch_size: int = Field(default=16, ge=1)


class GenerateGeneralistRequest(BaseModel):
    output_dir: str = Field(min_length=1)
    num_samples: int = Field(default=128, ge=1)
    min_bodies: int = Field(default=2, ge=2)
    max_bodies: int = Field(default=6, ge=2)
    dt_days: float = Field(default=1.0, gt=0.0)

    @model_validator(mode="after")
    def validate_body_range(self) -> Self:
        if self.max_bodies < self.min_bodies:
            raise ValueError("max_bodies must be greater than or equal to min_bodies")
        return self


class GenerateSpecialistRequest(BaseModel):
    output_dir: str = Field(min_length=1)
    fixture_name: str = Field(default="apophis/apophis_fixture.json", min_length=1)
    num_samples: int = Field(default=64, ge=1)
    dt_days: float = Field(default=1.0, gt=0.0)


class SimulateRequest(BaseModel):
    fixture_name: str = Field(default="apophis/apophis_fixture.json", min_length=1)
    steps: int = Field(default=30, ge=1)
    dt_days: float = Field(default=1.0, gt=0.0)
    checkpoint_path: str | None = Field(default=None, min_length=1)
    scaler_path: str | None = Field(default=None, min_length=1)
    ood_guard_path: str | None = Field(default=None, min_length=1)


class HealthResponse(BaseModel):
    status: str
    version: str
