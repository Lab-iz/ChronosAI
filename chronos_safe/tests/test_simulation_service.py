from chronos_safe.services.simulation import SimulationConfig, run_fixture_rollout, trajectory_payload


def test_simulation_service_builds_trajectory_payload() -> None:
    config = SimulationConfig(steps=2, dt_days=1.0)
    result = run_fixture_rollout(config)
    payload = trajectory_payload(result, dt_days=config.dt_days, source=config.fixture_name)

    assert payload["source"] == config.fixture_name
    assert payload["dt_days"] == config.dt_days
    assert payload["ids"]
    assert len(payload["frames"]) == config.steps + 1
