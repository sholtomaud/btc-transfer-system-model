
import pytest
import numpy as np
from models import CalibrationParams, Scenario
from simulation import SimulationEngine

def test_simulation_run():
    params = CalibrationParams(
        alpha=1.0, beta=0.5, lambda_val=1.0, kappa=0.5,
        theta=0.1, xi=0.05, sigma_0=0.02
    )
    scenario = Scenario(
        name="Test",
        duration_days=30,
        time_step_hours=24,
        initial_price=100.0,
        initial_liquidity=100.0,
        liquidity_trend=0.0,
        liquidity_volatility=0.0 # Deterministic liquidity
    )
    
    engine = SimulationEngine(params)
    results = engine.run_scenario(scenario)
    
    # We expect duration_days + 1 steps (including t=0)
    assert len(results.steps) == 31
    # Check initial state
    assert results.steps[0].price_p50 == 100.0
    assert results.steps[0].avg_liquidity == 100.0
    
    # Check bounds
    for r in results.steps:
        assert r.price_p50 > 0
        assert r.avg_liquidity > 0
        assert r.avg_volatility > 0

def test_simulation_determinism():
    params = CalibrationParams(
        alpha=1.0, beta=0.5, lambda_val=1.0, kappa=0.5,
        theta=0.1, xi=0.05, sigma_0=0.02
    )
    scenario = Scenario(name="Test", duration_days=10)
    
    engine1 = SimulationEngine(params)
    res1 = engine1.run_scenario(scenario)
    
    engine2 = SimulationEngine(params)
    res2 = engine2.run_scenario(scenario)
    
    # Since seed is set to 42 in run_scenario, results should be identical
    assert res1.steps[-1].price_p50 == res2.steps[-1].price_p50
