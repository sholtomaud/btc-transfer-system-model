# BTC Liquidity Transmission System

**Dynamic Systems Simulation & Forecasting Engine**

## Quick Start

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation
Install the project dependencies:
```bash
uv sync
```

### Running the Server
Start the development server with hot reload:
```bash
uv run uvicorn main:app --reload
```
The API will be available at [http://localhost:8000](http://localhost:8000).

### Running Tests
Execute the test suite:
```bash
uv run pytest
```

---

## Project Requirements

---

## 1. Purpose & Scope

This project implements a **dynamic systems-thinking simulation engine** for modeling and forecasting **BTCUSD price behavior** driven by:

* Global liquidity flows
* Sovereign & corporate debt refinancing cycles
* Supply inelasticity (halving effects)
* Reflexivity and market structure feedback loops

The system must support:

* Deterministic and stochastic simulation
* Scenario analysis
* Probabilistic forecasting with uncertainty bands
* Backtesting against historical data
* Real-time data ingestion
* Interactive visualization via **HTML + SVG + Web Components (no third-party JS libraries)**

The system is intended for:

* Macro-financial research
* Regime-change modeling
* Risk analysis
* Strategy development
* Educational and exploratory simulation

---

## 2. System Architecture Overview

```
┌────────────────────────────┐
│  External Data Sources     │
│  - BTC Exchanges           │
│  - FRED / Macro APIs       │
│  - Treasury Data           │
│  - RRP / Fed Balance Sheet │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│  Data Ingestion Layer      │
│  - Streaming (WebSocket)  │
│  - Batch ingestion         │
│  - Caching + validation    │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│  Simulation Engine         │
│  - Dynamic system model    │
│  - Stochastic modeling     │
│  - Scenario execution      │
│  - Monte Carlo simulation  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│  Forecasting & Backtest    │
│  - Model fitting           │
│  - Cross-validation        │
│  - Prediction envelopes    │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│  Visualization Server      │
│  - WebSocket API           │
│  - SVG streaming plots     │
│  - Interactive scenarios   │
└────────────────────────────┘
```

---

## 3. Core Conceptual Model

### 3.1 System Equation (Conceptual)

BTC price is modeled as a **nonlinear dynamic response system**:

```
BTC(t) = f(
    GlobalLiquidity(t),
    ΔLiquidity(t),
    DebtRefinancingCycle(t),
    SupplyInelasticity(t),
    Reflexivity(t),
    RiskSentiment(t)
)
```

Where:

* `GlobalLiquidity(t)` → Net financial liquidity available to risk assets
* `ΔLiquidity(t)` → First derivative of liquidity (impulse)
* `DebtRefinancingCycle(t)` → Structural macro timing cycle
* `SupplyInelasticity(t)` → Halving-driven supply rigidity
* `Reflexivity(t)` → Price → sentiment → capital feedback loops
* `RiskSentiment(t)` → Risk-on/off regime weighting

---

### 3.2 State Variables

| Variable | Description                     |
| -------- | ------------------------------- |
| L(t)     | Net global liquidity index      |
| dL/dt    | Liquidity impulse               |
| D(t)     | Debt cycle phase (0–1)          |
| S(t)     | Supply inelasticity coefficient |
| R(t)     | Reflexivity multiplier          |
| V(t)     | Market volatility               |
| P(t)     | BTCUSD price                    |

---

### 3.3 System Dynamics

The model must support:

* Coupled nonlinear differential equations
* Stochastic perturbations
* Delay terms (liquidity transmission lag)
* Regime switching (risk-on / risk-off states)

---

## 4. Simulation Engine Requirements

### 4.1 Deterministic Simulation

* Discrete time-step integration
* Configurable timestep (minutes → months)
* Support for:

  * Euler
  * Runge–Kutta 4
  * Adaptive step solvers

---

### 4.2 Stochastic Modeling

* Brownian noise injection
* Jump diffusion processes
* Fat-tailed distributions
* Correlated variable noise

---

### 4.3 Monte Carlo Engine

* ≥ 10,000 path simulations
* Parallel execution
* Probability envelope extraction:

  * P10
  * P25
  * P50
  * P75
  * P90

---

### 4.4 Scenario Modeling

Scenarios must be definable as structured parameter sets:

```yaml
scenario:
  name: Liquidity Surge + Regulatory Clarity
  liquidity_impulse: +750B
  debt_cycle_phase: 0.85
  reflexivity_gain: 1.8
  volatility_regime: medium
```

Capabilities:

* Batch scenario execution
* Comparative overlay plotting
* Regime stress testing
* Tail-risk scenario generation

---

## 5. Prediction & Forecasting Requirements

### 5.1 Forecast Horizon

* Intraday (minutes–hours)
* Short-term (days–weeks)
* Medium-term (months)

---

### 5.2 Probabilistic Forecasting

* Output full predictive distributions
* Produce uncertainty bands:

  * ±1σ
  * ±2σ
  * Tail probabilities

---

### 5.3 Regime Detection

* Identify:

  * Liquidity expansion
  * Liquidity contraction
  * Volatility compression
  * Volatility expansion

---

## 6. Backtesting Framework

### 6.1 Historical Data Replay

* Deterministic replay of past liquidity cycles
* Step-by-step causal replay

---

### 6.2 Performance Metrics

* Mean absolute error (MAE)
* Root mean square error (RMSE)
* Directional accuracy
* Turning-point detection accuracy
* Regime classification accuracy

---

### 6.3 Validation Modes

* Walk-forward validation
* Rolling window backtests
* Regime-isolated backtests

---

## 7. Data Ingestion Requirements

### 7.1 Market Data

* Real-time BTCUSD via WebSocket
* Multiple exchange subscription support
* Failover + redundancy

---

### 7.2 Macro Data

* Fed balance sheet
* Treasury General Account (TGA)
* Reverse repo facility (RRP)
* Global M2 liquidity proxies

---

### 7.3 Internal Data Normalization

* Unified time base
* Resampling
* Missing data interpolation
* Outlier detection

---

## 8. Server & API Layer

### 8.1 WebSocket Streaming API

Must support:

* Live price streaming
* Scenario updates
* Real-time forecast push
* Uncertainty band streaming

---

### 8.2 REST Control API

* Start/stop simulation
* Scenario upload
* Backtest execution
* Forecast retrieval

---

## 9. Visualization Requirements (HTML + SVG Only)

### 9.1 Rendering

* SVG-based timeseries plotting
* Dynamic axis scaling
* Zoom & pan
* Multiple scenario overlays

---

### 9.2 Plot Types

* Price time series
* Liquidity impulse
* Debt cycle phase
* Volatility regime
* Probability fan charts

---

### 9.3 Interaction

* Scenario sliders
* Live parameter tuning
* Monte Carlo replay
* Regime toggles

---

### 9.4 Security Constraints

* ❌ No third-party JS libraries
* ✔ Native Web Components only
* ✔ Pure DOM + SVG

---

## 10. Real-Time Trading Feed Integration

### 10.1 Exchange Connectivity

* Binance
* Coinbase
* Kraken

Via:

* Native WebSocket
* Failover handling
* Rate limiting

---

### 10.2 Data Handling

* Tick aggregation
* Microstructure smoothing
* Latency compensation

---

## 11. Configuration & Extensibility

### 11.1 Configuration Files

* YAML-based
* Hot reload

---

### 11.2 Plugin Architecture

* Liquidity model plugins
* Reflexivity models
* Alternative volatility models

---

## 12. Security Requirements

* Input validation
* Scenario sandboxing
* API rate limiting
* WebSocket authentication
* Deterministic replay isolation

---

## 13. Performance Requirements

| Component         | Target   |
| ----------------- | -------- |
| Simulation step   | < 5 ms   |
| Monte Carlo (10k) | < 2 sec  |
| WebSocket latency | < 100 ms |
| SVG redraw        | < 16 ms  |

---

## 14. Output Formats

* JSON (API)
* CSV (backtest)
* SVG (plots)
* Binary state snapshots

---

## 15. Implementation Language & Constraints

* Python 3.11+
* Async-first architecture
* Deterministic numerical kernels
* No external JS plotting libs

---

## 16. Research Extensions (Future Work)

* Multi-asset liquidity transmission modeling
* Cross-asset contagion simulation
* Stablecoin liquidity routing analysis
* On-chain liquidity feedback modeling

---

## 17. Design Philosophy

This system must be:

* Mechanistic, not narrative
* Causality-driven, not correlation-driven
* Systems-theoretic, not single-factor
* Regime-aware, not static

---

## 18. Core Principle

> Bitcoin is modeled not as a speculative asset, but as a **liquidity transmission system embedded within the global macro-financial engine**.

---

## 19. Deliverable

A deterministic + stochastic dynamic simulation engine capable of:

* Explaining historical BTC price behavior
* Forecasting future regimes
* Stress-testing macro scenarios
* Visualizing uncertainty-aware outcomes

---

**End of Requirements**
