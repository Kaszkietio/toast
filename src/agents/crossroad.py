from collections import defaultdict
import random
from mesa import Agent, Model
from .edge import Edge  # Assuming you have an Edge class defined elsewhere
from math import ceil

class CrossroadAgent(Agent):
    def __init__(
            self,
            unique_id: int,
            model: Model,
            incoming_edges: list[Edge],
            outgoing_edges: list[Edge]
        ):
        super().__init__(model)
        self.unique_id = unique_id

        print(f"[{self.unique_id}] Initializing CrossroadAgent with {len(incoming_edges)} incoming edges and {len(outgoing_edges)} outgoing edges")

        self.incoming_roads = {edge.source: 0 for edge in incoming_edges}  # Incoming neighbor agent ID -> number of cars
        # print(f"[{self.unique_id}] Incoming roads: {self.incoming_roads}")
        self.outgoing_roads = [edge.target for edge in outgoing_edges] # Outgoing neighbor agent IDs
        # print(f"[{self.unique_id}] Outgoing roads: {self.outgoing_roads}")

        self.light_durations = {edge.source: edge.light_duration for edge in incoming_edges}  # Incoming neighbor agent ID -> duration (sec)
        # print(f"[{self.unique_id}] Light durations: {self.light_durations}")
        self.car_throughput = {edge.target: edge.throughput for edge in outgoing_edges}  # Outgoing neighbor agent ID -> cars per second
        # print(f"[{self.unique_id}] Car throughput: {self.car_throughput}")

        self.green_light_index = -1  # Direction ID or name
        self.green_light_name = None  # Name of the current green light direction
        self.green_light_time_left = 0  # Time left for green light


    def step(self, delta: float):
        cars_passed = defaultdict(int)

        # if self.unique_id == 5:
        #     print(f"[{self.unique_id}] Starting step with delta: {delta} seconds")

        # 1. Compute how many cars can pass through the green light
        while delta > 0.0:
            if self.green_light_time_left <= 0.0:
                self.adjust_lights()
                # Switch to next green light
                self.green_light_index = (self.green_light_index + 1) % len(self.light_durations)
                self.green_light_name = list(self.light_durations.keys())[self.green_light_index]
                if self.unique_id == 1:
                    print(f"[{self.unique_id}] Switching green light to index {self.green_light_index} ({self.green_light_name}:{self.light_durations[self.green_light_name]} seconds)")
                self.green_light_time_left = self.light_durations[self.green_light_name]
                # if self.unique_id == 5:
                #     print(f"[{self.unique_id}] Switching green light to {self.green_light_name} for {self.green_light_time_left} seconds")

            passed_time = min(delta, self.green_light_time_left)
            delta -= passed_time
            self.green_light_time_left -= passed_time

            # 2. Calculate how many cars can pass
            random.shuffle(self.outgoing_roads)
            for road_id in self.outgoing_roads:
                throughput = self.car_throughput[road_id]
                max_passsed = min(int(ceil(throughput * passed_time)),
                                  self.incoming_roads[self.green_light_name])
                cars_passed[road_id] += max_passsed
                # Update the number of cars in the incoming roads
                self.incoming_roads[self.green_light_name] -= max_passsed

        # print(f"[{self.unique_id}] passed cars: {cars_passed}")
        # 4. Pass cars to other agents
        for road_id, cars in cars_passed.items():
            if cars > 0:
                neighbor_agent: CrossroadAgent = self.model.agents[road_id]
                neighbor_agent.receive_traffic(self.unique_id, cars)

        # print(f"[{self.unique_id}] Received traffic: {self.incoming_roads}")
        self.incoming_traffic = sum(self.incoming_roads.values())

    def receive_traffic(self, road_id: int, num_cars: int):
        self.incoming_roads[road_id] += num_cars

    # def observe_traffic(self):
    #     # Placeholder for actual sensing logic
    #     self.incoming_traffic = sum(self.incoming_roads.values())

    def communicate(self):
        # Communicate traffic info to neighbors
        for neighbor in self.neighbors:
            neighbor.receive_traffic_info(self.unique_id, self.incoming_traffic)

    def receive_traffic_info(self, sender_id, traffic_value):
        # Store info from neighbors
        pass  # You can store and average neighbor data

    def adjust_lights(self):
        # return
        # Simple adjustment logic (can use reinforcement learning later)
        # for src, traffic in self.incoming_roads.items():
        if self.green_light_name is None:
            return
        # print(f"[{self.unique_id}] Adjusting lights for {self.green_light_name} with current traffic: {self.incoming_roads[self.green_light_name]}")
        src = self.green_light_name
        traffic = self.incoming_roads[src]
        if traffic > 40:
            self.light_durations[src] += 1
            # print(f"[{self.unique_id}] Increasing light duration for {src} to {self.light_durations[src]} seconds due to high traffic ({traffic})")
        elif traffic < 5:
            self.light_durations[src] -= 1
            # print(f"[{self.unique_id}] Decreasing light duration for {src} to {self.light_durations[src]} seconds due to low traffic ({traffic})")

            # Ensure light durations are within reasonable limits
        self.light_durations[src] = min(max(1, self.light_durations[src]), 100)

    def get_light_status(self):
        links = []
        for edge in self.incoming_roads:
            links.append({
                "source": edge,
                "target": self.unique_id,
                "traffic": self.incoming_roads[edge],
                "green_light": (edge == self.green_light_name),
                "light_duration": self.light_durations[edge],
                "throughput": self.model.agents[edge].car_throughput[self.unique_id]
            })
        return links
