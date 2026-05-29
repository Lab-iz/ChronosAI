import pytest

from chronos_seguro.fisica.unidades import (
    au_to_meters,
    days_to_seconds,
    kg_to_solar_mass,
    meters_to_au,
    seconds_to_days,
    solar_mass_to_kg,
)


def test_distancia_volta_ao_valor_original() -> None:
    value = 123_456_789.0
    assert meters_to_au(au_to_meters(value)) == pytest.approx(value)


def test_tempo_volta_ao_valor_original() -> None:
    value = 3.5
    assert seconds_to_days(days_to_seconds(value)) == pytest.approx(value)


def test_massa_volta_ao_valor_original() -> None:
    value = 0.002
    assert kg_to_solar_mass(solar_mass_to_kg(value)) == pytest.approx(value)
