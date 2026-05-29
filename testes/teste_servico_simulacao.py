from chronos_seguro.servicos.simulacao import (
    ConfiguracaoSimulacao,
    executar_propagacao_cenario,
    montar_payload_trajetoria,
)


def test_servico_simulacao_monta_payload_trajetoria() -> None:
    config = ConfiguracaoSimulacao(steps=2, dt_days=1.0)
    result = executar_propagacao_cenario(config)
    payload = montar_payload_trajetoria(result, dt_days=config.dt_days, source=config.fixture_name)

    assert payload["source"] == config.fixture_name
    assert payload["dt_days"] == config.dt_days
    assert payload["ids"]
    assert len(payload["frames"]) == config.steps + 1
