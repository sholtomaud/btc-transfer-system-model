
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from models import CalibrationParams, SimulationState, Scenario, SimulationResult, MonteCarloStep

class SimulationEngine:
    def __init__(self, params: CalibrationParams):
        self.params = params

    def _dept_cycle(self, t_years: float) -> float:
        """
        D(t) = 0.5 * (1 + sin(2 * pi * t / Td + phi))
        """
        phase = 2 * np.pi * t_years / self.params.debt_cycle_period_years + self.params.debt_cycle_phase_offset
        return 0.5 * (1 + np.sin(phase))

    def _supply_inelasticity(self, t_years: float) -> float:
        """
        S(t) modeled as a step-like function increasing at 4-year intervals.
        Simplified: 1 + kappa * (current_halving_epoch)
        """
        return 1.0 + self.params.kappa * np.tanh(t_years / 4.0)

    def _reflexivity(self, current_log_price, prev_log_price, dt) -> float:
        """
        R = gamma * tanh(lambda * dx/dt)
        """
        if dt <= 0: return 0.0
        dx = current_log_price - prev_log_price
        return np.tanh(self.params.lambda_val * dx)

    def run_scenario(self, scenario: Scenario, historical_data: List[Dict] = None) -> SimulationResult:
        np.random.seed(42) # For reproducibility foundation, though paths will diverge

        # Time setup
        hours_per_year = 365.25 * 24
        dt_hours = scenario.time_step_hours
        dt_years = dt_hours / hours_per_year
        steps = int(scenario.duration_days * 24 / dt_hours)
        start_ts = pd.to_datetime(scenario.start_date).timestamp()
        
        num_paths = scenario.monte_carlo_paths

        # Arrays to store paths: [paths, steps + 1] (including t=0)
        price_paths = np.zeros((num_paths, steps + 1))
        liquidity_paths = np.zeros((num_paths, steps + 1))
        volatility_paths = np.zeros((num_paths, steps + 1))
        
        # Determine initial price
        # If historical_data is provided, try to find the price at start_date
        initial_price = scenario.initial_price
        if historical_data:
             # Find closest date
             start_date_str = scenario.start_date
             for rec in historical_data:
                 if rec['date'] == start_date_str:
                     initial_price = rec['price']
                     break
        
        initial_log_price = np.log(initial_price)
        
        for p in range(num_paths):
            current_log_price = initial_log_price
            current_liquidity = scenario.initial_liquidity
            current_volatility = self.params.sigma_0
            prev_log_price = current_log_price
            
            # Store initial state
            price_paths[p, 0] = initial_price
            liquidity_paths[p, 0] = current_liquidity
            volatility_paths[p, 0] = current_volatility

            liquidity_drift = scenario.liquidity_trend
            liquidity_vol = scenario.liquidity_volatility
            
            time_elapsed_years = 0.0

            for t in range(1, steps + 1):
                # 1. Update Liquidity
                dW_L = np.random.normal(0, np.sqrt(dt_years))
                dL = current_liquidity * (liquidity_drift * dt_years + liquidity_vol * dW_L)
                current_liquidity += dL
                
                # 2. Update Volatility Regime (OU Process)
                dW_vol = np.random.normal(0, np.sqrt(dt_years))
                d_sigma = self.params.theta * (self.params.sigma_0 - current_volatility) * dt_years + self.params.xi * dW_vol
                current_volatility += d_sigma
                current_volatility = max(0.001, current_volatility)
                
                # 3. Calculate Factors
                D_t = self._dept_cycle(time_elapsed_years)
                S_t = self._supply_inelasticity(time_elapsed_years)
                
                dx_prev = current_log_price - prev_log_price
                R_t = np.tanh(self.params.lambda_val * dx_prev)
                
                # 4. Price Update
                # Note: dL/current_liquidity is approx d(ln L)
                # alpha * D * S * d(ln L)
                liquidity_forcing = self.params.alpha * D_t * S_t * (dL / current_liquidity)
                
                # Beta * R * dt (Reflexivity drift)
                reflexivity_force = self.params.beta * R_t * dt_years
                
                # Sigma * dW
                dW_price = np.random.normal(0, np.sqrt(dt_years))
                stochastic_part = current_volatility * dW_price
                
                dx = liquidity_forcing + reflexivity_force + stochastic_part
                
                prev_log_price = current_log_price
                current_log_price += dx
                
                # Store results
                price_paths[p, t] = np.exp(current_log_price)
                liquidity_paths[p, t] = current_liquidity
                volatility_paths[p, t] = current_volatility
                
                time_elapsed_years += dt_years

        # Aggregation
        monte_carlo_steps = []
        for t in range(steps + 1):
            # Price percentiles
            prices_t = price_paths[:, t]
            p10 = float(np.percentile(prices_t, 10))
            p50 = float(np.percentile(prices_t, 50))
            p90 = float(np.percentile(prices_t, 90))
            
            # Averages for other metrics
            avg_liq = float(np.mean(liquidity_paths[:, t]))
            avg_vol = float(np.mean(volatility_paths[:, t]))
            
            # Timestamp
            ts = start_ts + t * dt_hours * 3600
            
            mc_step = MonteCarloStep(
                time_step=t,
                timestamp=ts,
                price_p10=p10,
                price_p50=p50,
                price_p90=p90,
                avg_liquidity=avg_liq,
                avg_volatility=avg_vol
            )
            monte_carlo_steps.append(mc_step)
            
        return SimulationResult(
            params=self.params,
            steps=monte_carlo_steps,
            history=historical_data if historical_data else []
        )
