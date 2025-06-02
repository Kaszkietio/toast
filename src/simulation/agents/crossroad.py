from mesa import Agent

class CrossroadAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.green_light_duration = 10  # seconds
        self.red_light_duration = 10
        self.incoming_traffic = 0
        self.neighbors = []

    def step(self):
        self.observe_traffic()
        self.communicate()
        self.adjust_lights()

    def observe_traffic(self):
        # Placeholder for actual sensing logic
        self.incoming_traffic = self.random.randint(0, 20)

    def communicate(self):
        # Communicate traffic info to neighbors
        for neighbor in self.neighbors:
            neighbor.receive_traffic_info(self.unique_id, self.incoming_traffic)

    def receive_traffic_info(self, sender_id, traffic_value):
        # Store info from neighbors
        pass  # You can store and average neighbor data

    def adjust_lights(self):
        # Simple adjustment logic (can use reinforcement learning later)
        if self.incoming_traffic > 15:
            self.green_light_duration += 1
            self.red_light_duration -= 1
