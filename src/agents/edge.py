class Edge:
    source: int
    target: int
    throughput: float
    light_duration: float

    def __init__(self, source: int, target: int, throughput: float, light_duration: float):
        self.source = source
        self.target = target
        self.throughput = throughput
        self.light_duration = light_duration