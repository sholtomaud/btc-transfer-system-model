
import random
import numpy as np
from deap import base, creator, tools, algorithms
from models import CalibrationParams, Scenario, OptimizationConfig
from simulation import SimulationEngine, SimulationResult
from history_loader import fetch_btc_history
from typing import List, Tuple

# Setup DEAP
# We want to maximize return (or minimize error if curve fitting)
# Let's assume we want to find params that maximize risk-adjusted return for now, 
# or fit a specific curve. The prompt mentions "guess optimal params".
# Let's make it flexible. For now: Maximize (Return / MaxDrawdown).
# Multi-objective: Max Return, Min Drawdown.

# Problem: We need to define Fitness weights dynamically based on objective 
# or create two types of creator. But DEAP creator is global.
# We will interpret the fitness values differently or return different metrics.
# 
# For Profit: Max Return (1.0), Min Drawdown (-1.0)
# For Calibration: Min MSE (-1.0), Min Drawdown (0.0? or just ignore 2nd obj)
# 
# A cleaner way is to stick to one standard, e.g., "Score".
# Profit Score = Return / (DD + 0.01)
# Calibration Score = -MSE

creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0)) # Max Return/Score, Min Drawdown/Error
creator.create("Individual", list, fitness=creator.FitnessMulti)

class GeneticOptimizer:
    def __init__(self, config: OptimizationConfig, scenario: Scenario, cache_duration_minutes: int = 60):
        self.config = config
        self.scenario = scenario
        self.toolbox = base.Toolbox()
        self.history = []
        if self.config.objective == "calibration":
            # Fetch history for calibration
            self.history = fetch_btc_history(start_date=scenario.start_date, cache_duration_minutes=cache_duration_minutes)
            
        self._setup_toolbox()

    def _setup_toolbox(self):
        # Attribute generator
        # Ranges for params: 
        # alpha [0.1, 5.0], beta [0.0, 1.0], lambda [0.1, 10.0], kappa [0.0, 1.0], 
        # theta [0.0, 1.0], xi [0.0, 0.5], sigma_0 [0.01, 0.1]
        
        self.toolbox.register("attr_alpha", random.uniform, 0.1, 5.0)
        self.toolbox.register("attr_beta", random.uniform, 0.0, 1.0)
        self.toolbox.register("attr_lambda", random.uniform, 0.1, 10.0)
        self.toolbox.register("attr_kappa", random.uniform, 0.0, 1.0)
        self.toolbox.register("attr_theta", random.uniform, 0.0, 2.0)
        self.toolbox.register("attr_xi", random.uniform, 0.0, 0.5)
        self.toolbox.register("attr_sigma0", random.uniform, 0.01, 0.15)
        
        # Structure initializer
        self.toolbox.register("individual", tools.initCycle, creator.Individual,
                             (self.toolbox.attr_alpha, self.toolbox.attr_beta, 
                              self.toolbox.attr_lambda, self.toolbox.attr_kappa,
                              self.toolbox.attr_theta, self.toolbox.attr_xi,
                              self.toolbox.attr_sigma0), n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        
        if self.config.objective == "calibration":
            self.toolbox.register("evaluate", self._evaluate_calibration)
        else:
            self.toolbox.register("evaluate", self._evaluate_profit)
            
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.1, indpb=0.2)
        # Check objective for selection strategy? NSGA2 is fine for multi-objective
        self.toolbox.register("select", tools.selNSGA2)

    def _decode_individual(self, individual) -> CalibrationParams:
        return CalibrationParams(
            alpha=abs(individual[0]),
            beta=abs(individual[1]),
            lambda_val=abs(individual[2]),
            kappa=abs(individual[3]),
            theta=abs(individual[4]),
            xi=abs(individual[5]),
            sigma_0=abs(individual[6])
        )

    def _run_sim(self, params) -> SimulationResult:
        opt_scenario = self.scenario.model_copy()
        opt_scenario.monte_carlo_paths = 1
        engine = SimulationEngine(params)
        # We pass history if available to align initial price, though simulation ignores history for logic
        return engine.run_scenario(opt_scenario, historical_data=self.history)

    def _evaluate_profit(self, individual):
        params = self._decode_individual(individual)
        results = self._run_sim(params)
        
        prices = [step.price_p50 for step in results.steps]
        if not prices: return -1.0, 1.0

        returns = (prices[-1] - prices[0]) / prices[0]
        
        peak = prices[0]
        max_dd = 0.0
        for p in prices:
            if p > peak: peak = p
            dd = (peak - p) / peak
            if dd > max_dd: max_dd = dd
            
        return returns, max_dd

    def _evaluate_calibration(self, individual):
        """
        Minimize MSE between P50 and Actual History.
        Secondary objective: Minimize Drawdown mismatch? Or just 0.
        """
        params = self._decode_individual(individual)
        results = self._run_sim(params)
        
        # Align simulation steps with history
        # History: list of {date, price}
        # Result: list of MonteCarloStep with timestamp
        
        if not self.history:
            return 0.0, 0.0 # Cannot calibrate without history
        
        total_sq_error = 0.0
        count = 0
        
        # Optimization: Create map of History Date -> Price
        hist_map = {h['date']: h['price'] for h in self.history}
        
        for step in results.steps:
            # Convert step timestamp to YYYY-MM-DD
            dt = step.timestamp
            import datetime
            date_str = datetime.datetime.fromtimestamp(dt).strftime('%Y-%m-%d')
            
            if date_str in hist_map:
                actual = hist_map[date_str]
                model = step.price_p50
                # Log error might be better for prices
                # err = (np.log(model) - np.log(actual)) ** 2
                err = (model - actual) ** 2
                total_sq_error += err
                count += 1
                
        if count == 0:
            return 1e9, 1e9 # Bad fit
            
        mse = total_sq_error / count
        rmse = np.sqrt(mse)
        
        # We want to MINIMIZE RMSE.
        # DEAP maximizes fitness by default?
        # weights=(1.0, -1.0).
        # We need to map RMSE to the first objective (1.0).
        # So we return -RMSE.
        
        return -rmse, 0.0

    def run(self) -> Tuple[List[float], float, float]:
        """
        Runs the GA optimization.
        Returns best params (list), return, drawdown
        """
        pop = self.toolbox.population(n=self.config.population_size)
        hof = tools.HallOfFame(1)
        
        algorithms.eaSimple(pop, self.toolbox, 
                            cxpb=self.config.crossover_rate, 
                            mutpb=self.config.mutation_rate, 
                            ngen=self.config.generations, 
                            halloffame=hof, 
                            verbose=False)
                            
        best_ind = hof[0]
        fitness = best_ind.fitness.values
        return list(best_ind), fitness[0], fitness[1]
