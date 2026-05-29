import pytest
from pydantic import ValidationError

from chronos_safe.apps.api.schemas import GenerateGeneralistRequest


def test_generalist_schema_rejects_invalid_body_range() -> None:
    with pytest.raises(ValidationError):
        GenerateGeneralistRequest(output_dir="data/processed/bad", min_bodies=5, max_bodies=3)
