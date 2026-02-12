
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
from typing import List

from models import CalibrationParams, Scenario, SimulationState, OptimizationConfig
from simulation import SimulationEngine
from optimizer import GeneticOptimizer

app = FastAPI(title="BTC Liquidity Transmission System")

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def get():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/simulate")
async def run_simulation(params: CalibrationParams, scenario: Scenario):
    engine = SimulationEngine(params)
    results = engine.run_scenario(scenario)
    return results

@app.post("/optimize")
async def optimize_parameters(config: OptimizationConfig, scenario: Scenario):
    optimizer = GeneticOptimizer(config, scenario)
    best_ind, ret, dd = optimizer.run()
    
    # Map back to params
    optimized_params = CalibrationParams(
        alpha=abs(best_ind[0]),
        beta=abs(best_ind[1]),
        lambda_val=abs(best_ind[2]),
        kappa=abs(best_ind[3]),
        theta=abs(best_ind[4]),
        xi=abs(best_ind[5]),
        sigma_0=abs(best_ind[6])
    )
    
    return {
        "params": optimized_params,
        "metrics": {
            "return": ret,
            "max_drawdown": dd
        }
    }

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Expect JSON with "action", "params", "scenario"
            payload = json.loads(data)
            action = payload.get("action")
            
            if action == "run_simulation":
                params_dict = payload.get("params")
                scenario_dict = payload.get("scenario")
                
                # Validate and parse
                # Note: This is synchronous, might block event loop if simulation is heavy.
                # In production, use a thread pool or run_in_executor.
                # For this demo, it executes fast enough (~seconds).
                
                try:
                    from history_loader import fetch_btc_history
                    
                    params = CalibrationParams(**params_dict)
                    scenario = Scenario(**scenario_dict)
                    
                    # Fetch history with configurable cache duration
                    # Default to 60 minutes if not provided
                    update_interval = payload.get("history_update_interval", 60)
                    history = fetch_btc_history(start_date=scenario.start_date, cache_duration_minutes=int(update_interval))
                    
                    engine = SimulationEngine(params)
                    results = engine.run_scenario(scenario, historical_data=history)
                    
                    # Stream results in chunks or all at once?
                    # Let's send all at once for simplicity, or stream if large.
                    # 10k steps might be largeish (10k objects).
                    # Let's send a summary or full data.
                    response = {
                        "type": "simulation_result",
                        "data": results.model_dump()
                    }
                    await websocket.send_text(json.dumps(response))
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
            
            elif action == "optimize":
                # Trigger optimization in background?
                # For websocket, maybe we want progress updates.
                # DEAP doesn't easily give callbacks without modifying algorithms.
                # We'll just run it and return.
                config_dict = payload.get("config")
                scenario_dict = payload.get("scenario")
                
                try:
                    config = OptimizationConfig(**config_dict)
                    scenario = Scenario(**scenario_dict)
                    
                    # Notify start
                    await websocket.send_text(json.dumps({"type": "info", "message": "Optimization started..."}))
                    
                    # Run in executor to avoid blocking
                    loop = asyncio.get_running_loop()
                    update_interval = payload.get("history_update_interval", 60)
                    optimizer = GeneticOptimizer(config, scenario, cache_duration_minutes=int(update_interval))
                    
                    # We wrap the synchronous run method
                    best_ind, ret, dd = await loop.run_in_executor(None, optimizer.run)
                    
                    optimized_params = CalibrationParams(
                        alpha=abs(best_ind[0]),
                        beta=abs(best_ind[1]),
                        lambda_val=abs(best_ind[2]),
                        kappa=abs(best_ind[3]),
                        theta=abs(best_ind[4]),
                        xi=abs(best_ind[5]),
                        sigma_0=abs(best_ind[6])
                    )
                    
                    response = {
                        "type": "optimization_result",
                        "params": optimized_params.model_dump(),
                        "metrics": {"return": ret, "max_drawdown": dd}
                    }
                    await websocket.send_text(json.dumps(response))
                    
                except Exception as e:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
