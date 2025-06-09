import random
from mesa import Model
from mesa.datacollection import DataCollector
from pydantic import BaseModel
import json

from agents.crossroad import CrossroadAgent
from agents.source import SourceAgent
from agents.sink import SinkAgent
from agents.edge import Edge
from agents.special_vehicle import SpecialVehicleAgent


class TrafficModel(Model):
    def __init__(self, nodes: list[int], links: dict[int, list[Edge]],
                 source: int, source_rate: float,
                 sink: int, sink_rate: float, seed=42,
                 special_vehicle_policy=lambda: True,
                 adjust_lights_policy=lambda: True):
        super().__init__(seed=seed)
        self.num_agents = len(nodes)
        self.nodes = nodes
        self.graph = links
        self.special_vehicles = 0
        self.source = source
        self.sink = sink
        self.websocket = None  # Placeholder for WebSocket connection
        self.current_time = 0.0
        self.finished_special_vehicles = []

        self.special_vehicle_policy = special_vehicle_policy
        self.adjust_lights_policy = adjust_lights_policy

        self.incoming_edges = {node: [] for node in self.nodes}
        for node, edges in self.graph.items():
            for edge in edges:
                self.incoming_edges[edge.target].append(edge)

        for node in self.nodes:
            if node == source:
                # Create a source agent
                agent = SourceAgent(node, self, source_rate, self.graph[node])
            elif node == sink:
                # Create a sink agent
                agent = SinkAgent(node, self, sink_rate, self.incoming_edges[node])
            else:
                # Create a regular crossroad agent
                agent = CrossroadAgent(node, self, self.incoming_edges[node], self.graph[node])
            self.agents.add(agent)

        print(f"Initialized TrafficModel with {self.num_agents} agents.")

        self.datacollector = DataCollector(
            model_reporters={
                "Time": lambda x: x.current_time,
                "TotalTraffic": self.compute_total_traffic,
                "AverageTraffic": self.compute_avg_traffic,
                "SpecialVehicles": self.process_finished_special_vehicles,
            }
        )


    def step(self, delta: float):
        self.current_time += delta
        self.datacollector.collect(self)
        # Step through all agents
        self.agents.shuffle_do("step", delta=delta)
        self.agents.do("advance")

    def get_traffic_update(self):
        nodes = self.nodes
        links = []
        special_vehicles = []

        for agent in self.agents:
            if isinstance(agent, CrossroadAgent):
                links.extend(agent.get_light_status())
            elif isinstance(agent, SpecialVehicleAgent):
                special_vehicles.append(agent)

        for vehicle in special_vehicles:
            for link in links:
                if link["source"] == vehicle.path[vehicle.current_index] and \
                   link["target"] == vehicle.path[vehicle.current_index + 1]:
                    print(f"Checking link {link['source']} -> {link['target']} for special vehicle {vehicle.unique_id}")
                    print(f"Vehicle path: {vehicle.path}, current index: {vehicle.current_index}")
                    link["special_vehicle"] = {
                        "time_left": vehicle.time_left_to_next,
                        "time_passed": vehicle.time_passed
                    }
                    print(f"Special vehicle {vehicle.unique_id} on link {link['source']} -> {link['target']}, "
                          f"time left: {vehicle.time_left_to_next:.2f}, time passed: {vehicle.time_passed:.2f}")
                    print(f"Link after update: {link}")
                    break

        return nodes, links

    def special_vehicle_reached_destination(self, vehicle: SpecialVehicleAgent):
        # Handle the special vehicle reaching its destination
        print(f"Special vehicle {vehicle.unique_id} reached its destination after {vehicle.time_passed:.2f} seconds.")
        if self.websocket:
            print(f"Sending WebSocket message for special vehicle {vehicle.unique_id} reaching destination.")
            self.websocket.send_text(json.dumps({
                "event": "special_vehicle_reached",
                "vehicle_id": vehicle.unique_id,
                "time_passed": vehicle.time_passed
            })).close()
        self.agents.remove(vehicle)
        self.finished_special_vehicles.append({"id": vehicle.unique_id, "time_passed": vehicle.time_passed})

    def add_special_vehicle(self):
        unique_id = -self.special_vehicles
        self.special_vehicles += 1
        vehicle = SpecialVehicleAgent(unique_id, self, self.find_random_path(self.source, self.sink))
        self.agents.add(vehicle)

    def find_random_path(self, source, sink):
        visited = set()
        path = []

        def dfs(node):
            if node == sink:
                path.append(node)
                return True
            visited.add(node)
            neighbors = list(self.graph[node])
            random.shuffle(neighbors)
            for neighbor in neighbors:
                if neighbor not in visited:
                    if dfs(neighbor.target):
                        path.append(node)
                        return True
            return False

        if dfs(source):
            return list(reversed(path))
        return []

    def compute_total_traffic(self):
        total = sum(agent.get_total_traffic() for agent in self.agents if isinstance(agent, CrossroadAgent))
        return total if self.agents else 0

    def compute_avg_traffic(self):
        total = [(agent.get_total_traffic(), len(agent.incoming_roads)) for agent in self.agents if isinstance(agent, CrossroadAgent)]
        averages = [traffic / count if count > 0 else 0 for traffic, count in total]
        return sum(averages) / len(averages) if len(averages) > 0 else 0

    def process_finished_special_vehicles(self):
        x = self.finished_special_vehicles
        self.finished_special_vehicles = []
        return x

    def set_adaptive_lights(self, enabled: bool):
        self.adjust_lights_policy = lambda: enabled


    def set_special_vehical_compliance(self, enabled: bool):
        self.special_vehicle_policy = lambda: enabled


    def simulate_accident(self, source: int, target: int):
        self.agents[source].accident_on_outgoing_road(target)
        self.agents[target].accident_on_incoming_road(source)