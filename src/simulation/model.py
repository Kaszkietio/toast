from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .agents.crossroad import CrossroadAgent

class TrafficModel(Model):
    def __init__(self, width, height, seed=42):
        super().__init__(seed=seed)
        self.num_agents = width * height
        self.grid = MultiGrid(width, height, torus=False)

        for i in range(self.num_agents):
            x = i % width
            y = i // width
            agent = CrossroadAgent(i, self)
            self.agents.add(agent)
            self.grid.place_agent(agent, (x, y))

        # Assign neighbors based on grid layout
        for agent in self.agents:
            x, y = agent.pos
            neighbors = self.grid.get_neighbors((x, y), moore=False, include_center=False)
            agent.neighbors = [a for a in neighbors if isinstance(a, CrossroadAgent)]

        self.datacollector = DataCollector(
            model_reporters={"AvgTraffic": self.compute_avg_traffic}
        )


    def step(self):
        self.datacollector.collect(self)
        # Step through all agents
        self.agents.do("step")
        self.agents.do("advance")


    def compute_avg_traffic(self):
        total = sum(agent.incoming_traffic for agent in self.agents)
        return total / len(self.agents) if self.agents else 0