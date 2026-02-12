
from simulation import SimulationEngine
from models import CalibrationParams, Scenario

params = CalibrationParams(
    alpha=1.0, beta=0.5, lambda_val=1.0, kappa=0.5,
    theta=0.1, xi=0.05, sigma_0=0.02
)
scenario = Scenario(
    name="Test",
    duration_days=10,
    time_step_hours=24,
    start_date="2025-01-01",
    monte_carlo_paths=5
)

engine = SimulationEngine(params)
result = engine.run_scenario(scenario)

print("Steps generated:", len(result.steps))
first_step = result.steps[0]
print("First step timestamp:", first_step.timestamp)
print("First step P50:", first_step.price_p50)
print("First step P10:", first_step.price_p10)
print("First step P90:", first_step.price_p90)
