from collections import defaultdict
from math import ceil
import random

from .crossroad import CrossroadAgent
from .edge import Edge  # Assuming you have an Edge class defined elsewhere

class SourceAgent(CrossroadAgent):
    def __init__(
        self,
        unique_id: int,
        model,
        rate: float,
        outgoing_edges: list[Edge]
    ):
        # Source has no incoming edges, just outgoing ones
        super().__init__(
            unique_id=unique_id,
            model=model,
            incoming_edges=[],
            outgoing_edges=outgoing_edges
        )
        self.rate = rate  # cars per second

    def step(self, delta: float):
        cars_passed = defaultdict(int)
        self.check_outgoing_accidents(delta)

        # Generate new cars to send through each outgoing edge
        random.shuffle(self.outgoing_roads)
        for edge in self.outgoing_roads:
            if edge in self.outgoing_accidents:
                # If there is an accident on this road, skip it
                print(f"[{self.unique_id}] Skipping road {edge} due to accident, time left: {self.outgoing_accidents[edge]['time_left']:.2f} seconds")
                continue
            new_cars = ceil(int(self.rate * delta))
            cars_passed[edge] += new_cars

        # Send cars to neighbors
        for road_id, cars in cars_passed.items():
            neighbor_agent = self.model.agents[road_id]
            neighbor_agent.receive_traffic(self.unique_id, cars)

    def change_light(self):
        return
