from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import numpy as np

class CalibrationParams(BaseModel):
    """
    Structural parameters for the BTC simulation model.
    """
    alpha: float = Field(..., description="Liquidity sensitivity")
    beta: float = Field(..., description="Reflexivity strength")
    lambda_val: float = Field(..., description="Reflexivity nonlinearity (lambda in Math.md)")
    kappa: float = Field(..., description="Halving amplification")
    theta: float = Field(..., description="Volatility mean reversion speed")
    xi: float = Field(..., description="Volatility randomness (vol of vol)")
    sigma_0: float = Field(..., description="Base volatility level")
    
    # Debt cycle parameters
    debt_cycle_period_years: float = Field(5.5, description="Period of the debt refinancing cycle in years")
    debt_cycle_phase_offset: float = Field(0.0, description="Phase offset for the debt cycle (phi)")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "alpha": 1.5,
                "beta": 0.3,
                "lambda_val": 2.0,
                "kappa": 0.5,
                "theta": 0.1,
                "xi": 0.05,
                "sigma_0": 0.02,
                "debt_cycle_period_years": 5.5,
                "debt_cycle_phase_offset": 0.0
            }
        }
    )

class SimulationState(BaseModel):
    """
    State of the system at a single time step t.
    """
    time_step: int
    timestamp: float # Unix timestamp
    price: float = Field(..., description="BTC Price P(t)")
    log_price: float = Field(..., description="Log price x(t)")
    liquidity: float = Field(..., description="Global liquidity index L(t)")
    liquidity_impulse: float = Field(..., description="Change in liquidity dL/dt")
    debt_cycle: float = Field(..., description="Debt cycle phase D(t) [0, 1]")
    supply_inelasticity: float = Field(..., description="Supply inelasticity S(t)")
    reflexivity: float = Field(..., description="Reflexivity component R(t)")
    volatility: float = Field(..., description="Current volatility regime sigma(t)")

class MonteCarloStep(BaseModel):
    """
    Aggregated stats for a single time step across N Monte Carlo paths.
    """
    time_step: int
    timestamp: float
    price_p10: float
    price_p50: float
    price_p90: float
    avg_liquidity: float
    avg_volatility: float

class SimulationResult(BaseModel):
    """
    Wrapper for simulation output.
    Can contain either a single deterministic path or Monte Carlo aggregates.
    """
    params: CalibrationParams
    steps: List[MonteCarloStep]
    history: List[Dict] = Field(default_factory=list, description="Historical actual prices [{'date': 'YYYY-MM-DD', 'price': 123.45}]")
    
class Scenario(BaseModel):
    """
    Configuration for a simulation run.
    """
    name: str
    start_date: str = Field("2023-01-01", description="Start date YYYY-MM-DD")
    duration_days: int = Field(365, description="Length of simulation in days")
    time_step_hours: float = Field(24.0, description="Size of each time step in hours")
    initial_price: float = Field(100000.0, description="Starting BTC price")
    initial_liquidity: float = Field(100.0, description="Starting liquidity index")
    
    monte_carlo_paths: int = Field(100, description="Number of paths for MC simulation")
    
    liquidity_trend: float = Field(0.05, description="Annualized trend in global liquidity")
    liquidity_volatility: float = Field(0.1, description="Annualized volatility of liquidity")

class OptimizationConfig(BaseModel):
    """
    Configuration for the Genetic Algorithm optimization.
    """
    population_size: int = Field(50, description="Number of individuals in population")
    generations: int = Field(20, description="Number of generations to evolve")
    mutation_rate: float = Field(0.2, description="Probability of mutation")
    crossover_rate: float = Field(0.5, description="Probability of crossover")
    target_return: float = Field(2.0, description="Target return multiple (e.g. 2.0x)")
    max_drawdown_limit: float = Field(0.3, description="Maximum acceptable drawdown")
    objective: str = Field("profit", description="'profit' or 'calibration'")
