
import pytest
from optimizer import GeneticOptimizer
from models import Scenario, OptimizationConfig
from history_loader import fetch_btc_history

@pytest.mark.slow
def test_calibration_optimizer():
    # 1. Fetch History
    history = fetch_btc_history(start_date="2024-01-01")
    if not history:
        pytest.skip("Could not fetch BTC history")

    # 2. Configure Optimizer
    scenario = Scenario(
        name="Test Calibration",
        start_date="2024-01-01",
        duration_days=30,
        monte_carlo_paths=2 # Low for speed
    )

    config = OptimizationConfig(
        population_size=4,
        generations=2,
        objective="calibration"
    )

    optimizer = GeneticOptimizer(config, scenario)
    best_params, score1, score2 = optimizer.run()

    assert best_params is not None
    assert score1 <= 0 # RMSE is negative
    assert score1 > -1e12
