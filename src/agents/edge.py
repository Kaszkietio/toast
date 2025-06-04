class Edge:
    source: int
    target: int
    throughput: float
    light_duration: float
    length: float

    def __init__(
            self,
            source: int,
            target: int,
            throughput: float,
            light_duration: float,
            length: float
    ):
        self.source = source
        self.target = target
        self.throughput = throughput
        self.light_duration = light_duration
        self.length = length