from mesa import Model
from mesa.datacollection import DataCollector
from pydantic import BaseModel

from agents.crossroad import CrossroadAgent
from agents.source import SourceAgent
from agents.sink import SinkAgent
from agents.edge import Edge


class TrafficModel(Model):
    def __init__(self, nodes: list[int], links: dict[int, list[Edge]],
                 source: int, source_rate: float,
                 sink: int, sink_rate: float, seed=42):
        super().__init__(seed=seed)
        self.num_agents = len(nodes)
        self.nodes = nodes
        self.graph = links

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

        # self.datacollector = DataCollector(
        #     model_reporters={"AvgTraffic": self.compute_avg_traffic}
        # )


    def step(self, delta: float):
        # self.datacollector.collect(self)
        # Step through all agents
        self.agents.shuffle_do("step", delta=delta)
        self.agents.do("advance")

    def get_traffic_update(self):
        nodes = self.nodes
        links = []
        for agent in self.agents:
            agent: CrossroadAgent
            links.extend(agent.get_light_status())

        return nodes, links

    # def compute_avg_traffic(self):
        # total = sum(agent.incoming_traffic for agent in self.agents)
        # return total / len(self.agents) if self.agents else 0