
from optimizer import GeneticOptimizer
from models import Scenario, OptimizationConfig
from history_loader import fetch_btc_history
import logging

logging.basicConfig(level=logging.INFO)

def test_calibration():
    print("Testing Calibration Logic...")
    
    # 1. Fetch History to ensure it works
    print("Fetching history...")
    history = fetch_btc_history(start_date="2023-01-01")
    if not history:
        print("ERROR: No history found.")
        return
    print(f"History records: {len(history)}")
    
    # 2. Configure Optimizer for Calibration
    scenario = Scenario(
        name="Test Calibration",
        start_date="2023-01-01",
        duration_days=365,
        monte_carlo_paths=10 # keeping it low for test speed
    )
    
    config = OptimizationConfig(
        population_size=5,
        generations=2,
        objective="calibration"
    )
    
    print("Initializing Optimizer...")
    optimizer = GeneticOptimizer(config, scenario)
    
    if not optimizer.history:
        print("ERROR: Optimizer did not load history.")
        return
        
    print("Running Optimization...")
    best_params, score1, score2 = optimizer.run()
    
    print(f"Best Params: {best_params}")
    print(f"Score (Negative RMSE): {score1}")
    print(f"Secondary Score: {score2}")
    
    if score1 > -1000000 and score1 <= 0:
        print("SUCCESS: Calibration ran and produced reasonable score.")
    else:
        print("WARNING: Score seems odd.")

if __name__ == "__main__":
    test_calibration()
