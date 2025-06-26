import asyncio
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from pydantic import BaseModel
import random
import threading
from typing import Optional
from typing import List

from model import TrafficModel
from graph import get_mid_graph

random.seed(42)

app = FastAPI()

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: int

class SpecialVehicleData(BaseModel):
    time_left: float
    time_passed: float

class Link(BaseModel):
    source: int
    target: int
    traffic: int
    green_light: bool
    light_duration: float
    throughput: float
    special_vehicle: Optional[SpecialVehicleData] = None


class GraphData(BaseModel):
    nodes: List[Node]
    links: List[Link]
    sources: List[int]
    sinks: List[int]


# Stable presentation
nodes, roads, sources, sinks = get_mid_graph()
traffic_model = TrafficModel(nodes, roads, sources, 17.5, sinks, 17.5)  # Adjust parameters as needed


graph_lock = threading.Lock()
graph_snapshot: Optional[GraphData] = None

async def run_simulation():
    while True:
        with graph_lock:
            traffic_model.step(0.1)  # Step the model
        await asyncio.sleep(0.1)  # Adjust the frequency of updates as needed

@app.on_event("startup")
async def startup_event():
    # Start the simulation in a separate thread
    print("Starting traffic simulation...")
    asyncio.create_task(run_simulation())

@app.websocket("/ws/traffic")
async def traffic_graph_endpoint(websocket: WebSocket):
    await websocket.accept()
    traffic_model.websocket = websocket  # Store the WebSocket connection in the model
    try:
        while True:
            msg = await websocket.receive_text()
            if msg != "get_graph":
                print("Received unexpected message:", msg)
                continue
            # Get the current state of the traffic graph
            with graph_lock:
                graph_snapshot = get_traffic_graph()
            await websocket.send_text(graph_snapshot.model_dump_json())
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        await websocket.close()
        raise e

@app.post("/spawn-ambulance")
def spawn_ambulance():
    traffic_model.add_special_vehicle()
    return {"status": "ok"}

last_metrics_time = -1.0

@app.get("/metrics")
def get_metrics():
    global last_metrics_time
    df = traffic_model.datacollector.get_model_vars_dataframe()
    special_vehicle_df = df.where(df["Time"] > last_metrics_time)["SpecialVehicles"].dropna()
    special_vehicles = []
    for l in special_vehicle_df.tolist():
        special_vehicles.extend(l)
    if special_vehicles:
        print(special_vehicles)
    last_metrics_time = df["Time"].iloc[-1].item() if not df.empty else -1.0
    return {
        "Time": last_metrics_time,
        "TotalTraffic":df["TotalTraffic"].iloc[-1].item(),
        "AverageWaitingTime": df["AverageWaitingTime"].iloc[-1].item(),
        "SpecialVehicles": special_vehicles,
    }


@app.post("/config/adaptive_lights")
def set_adaptive_lights(enabled: bool = Body(...)):
    traffic_model.set_adaptive_lights(enabled)
    return {"status": "ok", "adaptive_lights": enabled}


@app.post("/config/ambulance_priority")
def set_ambulance_priority(enabled: bool = Body(...)):
    traffic_model.set_special_vehical_compliance(enabled)
    return {"status": "ok", "ambulance_priority": enabled}

@app.post("/save/metrics")
def save_metrics():
    df = traffic_model.datacollector.get_model_vars_dataframe()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_path = os.path.join(__file__, "..", "metrics")
    os.makedirs(dir_path, exist_ok=True)
    df.to_csv(os.path.join(dir_path, f"{timestamp}.csv"))
    return {"status": "ok", "file": f"metrics_{timestamp}.csv"}


@app.post("/simulate-accident")
async def simulate_accident(link: dict):
    source, target = link.get("source"), link.get("target")
    traffic_model.simulate_accident(source, target)
    return {"status": "ok", "message": f"Accident simulated on link {source} -> {target}"}


@app.post("/config/accurate_special_vehicle_route")
def set_ambulance_priority(enabled: bool = Body(...)):
    traffic_model.set_special_vehicle_route_accuracy(enabled)
    return {"status": "ok", "route_accuracy": enabled}


def get_traffic_graph():
    nodes, links = traffic_model.get_traffic_update()

    nodes = [Node(id=node_id) for node_id in nodes]
    links = [
        Link(**edge)
        for edge in links
    ]

    return GraphData(nodes=nodes, links=links, sources=traffic_model.sources, sinks=traffic_model.sinks)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)