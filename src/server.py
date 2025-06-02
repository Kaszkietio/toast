import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
from typing import List
from simulation.model import TrafficModel  # Import your Mesa model
import random

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

class Link(BaseModel):
    source: int
    target: int
    traffic: int
    green_light: bool

class GraphData(BaseModel):
    nodes: List[Node]
    links: List[Link]

# Initialize the Mesa traffic model
# traffic_model = TrafficModel(4)  # Adjust parameters as needed

@app.websocket("/ws/traffic")
async def traffic_graph_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Get the current state of the traffic graph
            graph_data = get_traffic_graph()
            # Send the graph data as JSON
            s = graph_data.model_dump_json()
            print(f"Sending graph data: {s}")
            await websocket.send_text(graph_data.model_dump_json())
            await asyncio.sleep(1)  # Adjust the frequency of updates as needed
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


def get_traffic_graph():
    # Step the model once or return current state
    # traffic_model.step()

    # Extract nodes and links from the model
    # crossroads = traffic_model.get_crossroads()  # List of IDs
    # roads = traffic_model.get_roads()  # List of dicts with source, target, traffic

    crossroads = list(range(6))
    roads = {
        0: [(1, random.randint(0, 20), bool(random.randint(0, 1))), (2, random.randint(0, 20),bool(random.randint(0, 1)))],
        1: [(2, random.randint(0, 20), bool(random.randint(0, 1))), (3, random.randint(0, 20),bool(random.randint(0, 1)))],
        2: [(3, random.randint(0, 20), bool(random.randint(0, 1))), (1, random.randint(0, 20),bool(random.randint(0, 1)))],
        3: [(4, random.randint(0, 20), bool(random.randint(0, 1))), (5, random.randint(0, 20),bool(random.randint(0, 1)))],
        4: [(5, random.randint(0, 20), bool(random.randint(0, 1))), (3, random.randint(0, 20),bool(random.randint(0, 1)))],
        5: [],
    }

    nodes = [Node(id=cr_id) for cr_id in crossroads]
    links = []
    for source, neighbors in roads.items():
        if not neighbors:
            continue
        # Ensure neighbors are unique and sorted by traffic
        cur_links = [Link(source=source, target=neighbor[0], traffic=neighbor[1], green_light=neighbor[2]) for neighbor in neighbors]
        links.extend(cur_links)
    # links = [Link(source=source, target=neighbor[0], traffic=neighbor[1]) for source, neighbor in roads.items()]

    return GraphData(nodes=nodes, links=links)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)