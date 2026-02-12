
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
    
    assert len(results) == 30
    assert results[0].price == 100.0 # Wait, first result is usually t=0 or t=1?
    # Loop range(steps). If t=0 to 29.
    # Logic: current_price initialized. Loop updates it.
    # results stored at end of loop. So results[0] is t=0 after 1 step?
    # simulation.py: 
    # for t in range(steps): ... results.append(state)
    # state uses `t` (0 index) but price is updated.
    # So `results[0]` corresponds to t=0 (first step output).
    
    # Check bounds
    for r in results:
        assert r.price > 0
        assert r.liquidity > 0
        assert r.volatility > 0

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
    assert res1[-1].price == res2[-1].price
