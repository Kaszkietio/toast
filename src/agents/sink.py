from math import ceil

from .crossroad import CrossroadAgent
from .edge import Edge


class SinkAgent(CrossroadAgent):
    def __init__(
        self,
        unique_id: int,
        model,
        rate: float,
        incoming_edges: list[Edge]
    ):
        # Sink has only incoming edges, no outgoing ones
        super().__init__(
            unique_id=unique_id,
            model=model,
            incoming_edges=incoming_edges,
            outgoing_edges=[]
        )
        self.rate = rate
        self.total_received = 0

    def step(self, delta: float):
        # Just consume all incoming cars
        for src in self.incoming_roads:
            throughput = self.model.agents[src].car_throughput[self.unique_id]
            cars_received = min(int(ceil(throughput * delta)), self.incoming_roads[src])
            self.total_received += cars_received
            self.incoming_roads[src] -= cars_received

    def get_light_status(self):
        links = super().get_light_status()
        for link in links:
            link["green_light"] = True  # Sink does not control lights
        return links

    def is_light_green_for(self, road_id: int) -> bool:
        return True
