import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from typing import List
from model import TrafficModel  # Import your Mesa model
from agents.edge import Edge  # Import your Edge class
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

nodes=list(range(6))  # Example crossroads
roads = {
    0: [Edge(0, 1, random.normalvariate(20, 1.5), 5.0),
        Edge(0, 2, random.normalvariate(20, 1.5), 5.0),
    ],
    1: [
        # Edge(1, 2, random.normalvariate(20, 1.5), 5.0),
        Edge(1, 3, random.normalvariate(20, 1.5), 5.0)
    ],
    2: [Edge(2, 3, random.normalvariate(20, 1.5), 5.0),
        Edge(2, 1, random.normalvariate(20, 1.5), 5.0)
    ],
    3: [Edge(3, 4, random.normalvariate(20, 1.5), 5.0),
        Edge(3, 5, random.normalvariate(20, 1.5), 5.0)
    ],
    4: [Edge(4, 5, random.normalvariate(20, 1.5), 5.0),
        # Edge(4, 3, random.normalvariate(20, 1.5), 5.0)
    ],
    5: [],
}

traffic_model = TrafficModel(nodes, roads, 0, 5.0, 5, 5.0)  # Adjust parameters as needed
graph_lock = threading.Lock()
graph_snapshot: Optional[GraphData] = None

async def run_simulation():
    while True:
        with graph_lock:
            print("Simulation step..")
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
        print(f"WebSocket error: {e}")
        await websocket.close()


def get_traffic_graph():
    # Step the model once or return current state
    # traffic_model.step()

    nodes, links = traffic_model.get_traffic_update()

    nodes = [Node(id=node_id) for node_id in nodes]
    links = [
        Link(**edge)
        for edge in links
    ]
    # Extract nodes and links from the model
    # crossroads = traffic_model.get_crossroads()  # List of IDs
    # roads = traffic_model.get_roads()  # List of dicts with source, target, traffic

    # crossroads = list(range(6))
    # roads = {
    #     0: [(1, random.randint(0, 20), bool(random.randint(0, 1))), (2, random.randint(0, 20),bool(random.randint(0, 1)))],
    #     1: [(2, random.randint(0, 20), bool(random.randint(0, 1))), (3, random.randint(0, 20),bool(random.randint(0, 1)))],
    #     2: [(3, random.randint(0, 20), bool(random.randint(0, 1))), (1, random.randint(0, 20),bool(random.randint(0, 1)))],
    #     3: [(4, random.randint(0, 20), bool(random.randint(0, 1))), (5, random.randint(0, 20),bool(random.randint(0, 1)))],
    #     4: [(5, random.randint(0, 20), bool(random.randint(0, 1))), (3, random.randint(0, 20),bool(random.randint(0, 1)))],
    #     5: [],
    # }

    # nodes = [Node(id=cr_id) for cr_id in crossroads]
    # links = []
    # for source, neighbors in roads.items():
    #     if not neighbors:
    #         continue
    #     # Ensure neighbors are unique and sorted by traffic
    #     cur_links = [Link(source=source, target=neighbor[0], traffic=neighbor[1], green_light=neighbor[2]) for neighbor in neighbors]
    #     links.extend(cur_links)
    # links = [Link(source=source, target=neighbor[0], traffic=neighbor[1]) for source, neighbor in roads.items()]

    # print("Graph data prepared with nodes:", nodes, "and links:", links)

    return GraphData(nodes=nodes, links=links)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)