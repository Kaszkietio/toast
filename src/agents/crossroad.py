from collections import defaultdict
import random
from mesa import Agent, Model
from .edge import Edge  # Assuming you have an Edge class defined elsewhere
from math import ceil

ACCIDENT_DURATION = 30.0  # seconds

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

        # Incoming neighbor agent ID -> number of cars
        self.incoming_roads = {edge.source: 0 for edge in incoming_edges}
        # Incoming neighbor agent ID -> road length
        self.incoming_roads_lengths = {edge.source: edge.length for edge in incoming_edges}
        # Outgoing neighbor agent IDs
        self.outgoing_roads = [edge.target for edge in outgoing_edges]

        # Incoming neighbor agent ID -> duration (sec)
        self.light_durations = {edge.source: edge.light_duration for edge in incoming_edges}
        # Incoming neighbor agent ID -> initial duration (sec)
        self.initial_light_durations = self.light_durations.copy()
        # Outgoing neighbor agent ID -> cars per second
        self.car_throughput = {edge.target: edge.throughput for edge in outgoing_edges}

        # Direction ID or name
        self.green_light_index = -1
        # Name of the current green light direction
        self.green_light_name = None
        # Time left for green light
        self.green_light_time_left = 0
        self.change_light()

        # Used for special vehicles to override the light cycle
        self.light_cycle = None

        # Outgoing road ID -> number of cars waiting due to accidents
        self.outgoing_accidents = {}
        # Incoming road ID -> number of cars waiting due to accidents
        self.incoming_accidents = {}

    def step(self, delta: float):
        cars_passed = defaultdict(int)
        additional_cars = 0

        self.adjust_lights()
        # 1. Compute how many cars can pass through the green light
        while delta > 0.0:

            if self.green_light_time_left <= 0.0:
                self.change_light()

            passed_time = min(delta, self.green_light_time_left)
            delta -= passed_time
            self.green_light_time_left -= passed_time

            self.check_outgoing_accidents(passed_time)
            self.check_incoming_accidents(passed_time)

            if len(self.outgoing_roads) == len(self.outgoing_accidents):
                return

            # 2. Calculate how many cars can pass
            random.shuffle(self.outgoing_roads)
            for road_id in self.outgoing_roads:
                if road_id in self.outgoing_accidents:
                    throughput = self.outgoing_accidents[road_id]["throughput"]
                    max_passsed = min(int(ceil(throughput * passed_time)),
                                  self.incoming_roads[self.green_light_name])
                    additional_cars += max_passsed
                    continue

                throughput = self.car_throughput[road_id]
                max_passsed = min(int(ceil(throughput * passed_time)),
                                  self.incoming_roads[self.green_light_name])
                cars_passed[road_id] += max_passsed
                # Update the number of cars in the incoming roads
                self.incoming_roads[self.green_light_name] -= max_passsed

        additional_cars_per_road = additional_cars // (len(self.outgoing_roads) - len(self.outgoing_accidents))

        # 4. Pass cars to other agents
        for road_id, cars in cars_passed.items():
            if road_id in self.outgoing_accidents:
                continue
            if cars > 0:
                neighbor_agent: CrossroadAgent = self.model.agents[road_id]
                neighbor_agent.receive_traffic(self.unique_id, cars)
                neighbor_agent.receive_traffic(self.unique_id, additional_cars_per_road)


        self.incoming_traffic = sum(self.incoming_roads.values())


    def receive_traffic(self, road_id: int, num_cars: int):
        self.incoming_roads[road_id] += num_cars


    def communicate(self):
        # Communicate traffic info to neighbors
        for neighbor in self.neighbors:
            neighbor.receive_traffic_info(self.unique_id, self.incoming_traffic)


    def adjust_lights(self):
        if not self.model.adjust_lights_policy():
            return
        # Simple adjustment logic (can use reinforcement learning later)
        if self.green_light_name is None:
            return
        for src in self.incoming_roads:
            if src == self.green_light_name:
                continue
            if src in self.incoming_accidents:
                # Skip roads with accidents
                continue
            traffic = self.incoming_roads[src]
            if traffic > 80:
                self.light_durations[src] += (traffic - 80) / 20.0 * 0.01 + 0.01
            elif traffic < 20:
                self.light_durations[src] -= (20 - traffic) / 10 * (0.1 - 0.01) + 0.01

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


    def get_total_traffic(self) -> int:
        return sum(self.incoming_roads.values())


    def get_traffic(self, road_id: int) -> int:
        return self.incoming_roads[road_id]


    def get_throughput(self, road_id: int) -> float:
        return self.car_throughput[road_id]


    def get_road_length(self, road_id: int) -> float:
        return self.incoming_roads_lengths[road_id]


    def change_light(self, road_id: int | None = None):
        print(f"[{self.unique_id}] Changing light for road {road_id} (current green: {self.green_light_name})")
        if road_id is None:
            self.green_light_index = (self.green_light_index + 1) % len(self.light_durations)
        else:
            self.green_light_index = list(self.light_durations.keys()).index(road_id)
        print(f"\t[{self.unique_id}] New green light index: {self.green_light_index}")
        self.green_light_name = list(self.light_durations.keys())[self.green_light_index]
        self.green_light_time_left = self.light_durations[self.green_light_name]


    def override_light_for(self, road_id: int):
        if self.model.special_vehicle_policy():
            self.light_cycle = self.green_light_name
            self.change_light(road_id)
            # Override light to be green indefinitely
            self.green_light_time_left = float('inf')
            print(f"1###############[{self.unique_id}] SWITCHED green light: "\
                  f"{self.green_light_name}:{self.green_light_time_left} seconds left")


    def return_to_light_cycle(self):
        if self.light_cycle is not None:
            print(f"[{self.unique_id}] Returning to light cycle: {self.light_cycle}")
            self.change_light(self.light_cycle)
            self.light_cycle = None
            print(f"2###############[{self.unique_id}] SWITCHED green light: "\
                  f"{self.green_light_name}:{self.green_light_time_left} seconds left")


    def is_light_green_for(self, road_id: int) -> bool:
        print(f"[{self.unique_id}] Checking if light is green for {road_id}:"\
               f"{self.green_light_name == road_id}")
        print(f"[{self.unique_id}] Current green light: {self.green_light_name}:"\
              f"{self.green_light_time_left} seconds left")
        return self.green_light_name == road_id


    def accident_on_outgoing_road(self, road_id: int):
        self.outgoing_accidents[road_id] = {
            "time_left": ACCIDENT_DURATION,
            "throughput": self.car_throughput[road_id],
        }
        # No cars can pass through this road
        self.car_throughput[road_id] = 0


    def accident_on_incoming_road(self, road_id: int):
        self.incoming_accidents[road_id] = {
            "time_left": ACCIDENT_DURATION,
        }


    def check_outgoing_accidents(self, delta: float):
        # Check outgoing roads for accidents
        for road_id in list(self.outgoing_accidents.keys()):
            self.outgoing_accidents[road_id]["time_left"] -= delta
            if self.outgoing_accidents[road_id]["time_left"] <= 0:
                self.car_throughput[road_id] = self.outgoing_accidents[road_id]["throughput"]
                self.outgoing_accidents.pop(road_id)


    def check_incoming_accidents(self, delta: float):
        for road_id in list(self.incoming_accidents.keys()):
            self.incoming_accidents[road_id]["time_left"] -= delta
            if self.incoming_accidents[road_id]["time_left"] <= 0:
                self.light_durations[road_id] = self.initial_light_durations[road_id]
                self.incoming_accidents.pop(road_id)


    def get_time_to_reach_dest(self, prev: int, dest: int, route: list[int]) -> tuple[float, list[int]]:
        if self.unique_id in route:
            print(f"[{self.unique_id}] Already visited in route, returning infinite time")
            return (float('inf'), [])
        print(f"[{self.unique_id}] Getting time to reach destination")
        best_route = []
        best_time = float('inf')
        for neighbor_id in self.outgoing_roads:
            if neighbor_id == prev:
                continue
            print(f"[{self.unique_id}] Checking neighbor {neighbor_id} for best route")
            throughput = self.get_throughput(neighbor_id)
            neighbor: CrossroadAgent = self.model.agents[neighbor_id]
            traffic = neighbor.get_traffic(self.unique_id)
            road_length = neighbor.get_road_length(self.unique_id)
            additional_time = self.model.get_time_to_pass_road(road_length, traffic, throughput)
            cur_time, cur_route = neighbor.get_time_to_reach_dest(self.unique_id, dest, route + [self.unique_id])
            cur_time += additional_time
            if cur_time < best_time:
                best_time = cur_time
                best_route = [self.unique_id] + cur_route

        print(f"[{self.unique_id}] Best route: {best_route} with time: {best_time:.2f} seconds")
        return (best_time, best_route)