from mesa import Agent

from .crossroad import CrossroadAgent

class SpecialVehicleAgent(Agent):
    def __init__(self, unique_id: int, model, path: list[int]):
        super().__init__(model)
        self.unique_id = unique_id
        # List of node (crossroad) IDs
        self.path = path
        self.current_index = -1
        # Time left to reach the next node
        self.time_left_to_next = 0.0
        # Total time passed since the vehicle started moving
        self.time_passed = 0.0
        print(f"[{self.unique_id}] Initializing SpecialVehicleAgent with path: {self.path}")
        self.move_to_next_node()
        self.request_light_override()

    def step(self, delta: float):
        while delta > 0.0:
            print(f"[{self.unique_id}] Time left to next: {self.time_left_to_next:.2f} seconds")
            if self.time_left_to_next <= 0.0:
                # Inform the current crossroad that the vehicle is passing
                current_node_id = self.path[self.current_index]
                current_node: CrossroadAgent = self.model.agents[current_node_id]
                current_node.return_to_light_cycle()

                # Move to the next node
                self.move_to_next_node()
                if self.current_index == len(self.path) - 1:
                    break

                # Request override light for the next node
                self.request_light_override()

            if self.is_green_light():
                passed_time = min(delta, self.time_left_to_next)
                delta -= passed_time
                self.time_passed += passed_time
                self.time_left_to_next -= passed_time
            else:
                # Wait for the green light
                self.time_passed += delta
                self.time_left_to_next -= delta*0.1
                return


        if self.current_index == len(self.path)  - 1:
            print(f"[{self.unique_id}] Reached destination at {self.path[-1]} "\
                  f"after {self.time_passed:.2f} seconds")
            self.model.special_vehicle_reached_destination(self)
            return  # Reached destination

    def move_to_next_node(self):
        self.current_index += 1
        if self.current_index == len(self.path) - 1:
            return

        current_node_id = self.path[self.current_index]
        next_node_id = self.path[self.current_index + 1]

        print(self.model.agents[next_node_id].incoming_roads)

        prev_crossroad: CrossroadAgent = self.model.agents[current_node_id]
        next_crossroad: CrossroadAgent = self.model.agents[next_node_id]
        throughput = prev_crossroad.car_throughput[next_node_id]
        traffic = next_crossroad.get_traffic(current_node_id)
        road_length = next_crossroad.get_road_length(current_node_id)

        self.time_left_to_next = self.model.get_time_to_pass_road(
            throughput=throughput,
            traffic=traffic,
            road_length=road_length
        )

        print(f"[{self.unique_id}] Time left to next node {next_node_id}:"\
              f" {self.time_left_to_next:.2f} seconds")


    def is_green_light(self):
        current_node_id = self.path[self.current_index]
        next_node_id = self.path[self.current_index + 1]

        # Check if the light is green for the current direction
        current_crossroad: CrossroadAgent = self.model.agents[next_node_id]
        return current_crossroad.is_light_green_for(current_node_id)

    def request_light_override(self):
        current_node_id = self.path[self.current_index]
        next_node_id = self.path[self.current_index + 1]

        # Request the current crossroad to override the light for this vehicle
        current_crossroad: CrossroadAgent = self.model.agents[next_node_id]
        current_crossroad.override_light_for(current_node_id)