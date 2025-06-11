import random
from agents.edge import Edge


def get_big_graph():
    highway_throughput = 30.0
    inner_city_throughput = 5.0
    nodes = list(range(18))  # Example crossroads
    roads = {
        # Source
        0: [
            # Edge(source=0, target=1,  length=30.0, light_duration=30.0, throughput=highway_throughput),
            # Edge(source=0, target=4,  length=30.0, light_duration=30.0, throughput=highway_throughput),
            Edge(source=0, target=7,  length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=0, target=12, length=5.0, light_duration=5.0, throughput=5.0),
        ],
        # Highway
        1: [
            Edge(source=1, target=2,   length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=1, target=7,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        2: [
            Edge(source=2, target=3,   length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=2, target=9,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        3: [
            Edge(source=3, target=17,  length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=3, target=11,  length=5.0,  light_duration=5.0,  throughput=5.0),

            # Sink
            Edge(source=3,  target=17, length=30.0, light_duration=30.0, throughput=highway_throughput),
        ],

        # Highway
        4: [
            Edge(source=4, target=5,   length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=4, target=12,  length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        5: [
            Edge(source=5, target=6,   length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=5, target=14,  length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        6: [
            Edge(source=6, target=17,   length=30.0, light_duration=20.0, throughput=highway_throughput),
            Edge(source=6, target=16,   length=5.0,  light_duration=5.0,  throughput=5.0),

            # Sink
            Edge(source=6,  target=17, length=30.0, light_duration=30.0, throughput=highway_throughput),
        ],

        # Inner city
        7: [
            Edge(source=7, target=1,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=7, target=8,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=7, target=12,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        8: [
            Edge(source=8, target=9,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=8, target=13,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        9: [
            Edge(source=9, target=2,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=9, target=10,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=9, target=14,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        10: [
            Edge(source=10, target=11,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        11: [
            Edge(source=11, target=3,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=11, target=16,   length=5.0,  light_duration=5.0,  throughput=5.0),

            # Sink
            Edge(source=11, target=17, length=5.0,  light_duration=5.0,  throughput=5.0),
        ],


        12: [
            Edge(source=12, target=4,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=12, target=7,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=12, target=13,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        13: [
            Edge(source=13, target=8,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=13, target=14,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        14: [
            Edge(source=14, target=5,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=14, target=9,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=14, target=15,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        15: [
            Edge(source=15, target=10,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=15, target=16,   length=5.0,  light_duration=5.0,  throughput=5.0),
        ],
        16: [
            Edge(source=16, target=6,   length=5.0,  light_duration=5.0,  throughput=5.0),
            Edge(source=16, target=11,   length=5.0,  light_duration=5.0,  throughput=5.0),

            # Sink
            Edge(source=16, target=17, length=5.0,  light_duration=5.0,  throughput=5.0),
        ],

        # Sink
        17: []
    }
    return nodes, roads


def get_small_graph():
    nodes=list(range(6))  # Example crossroads
    roads = {
        0: [Edge(0, 1, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(0, 2, random.normalvariate(20, 1.5), 5.0, 5.0),
        ],
        1: [
            # Edge(1, 2, random.normalvariate(20, 1.5), 5.0),
            Edge(1, 3, random.normalvariate(20, 1.5), 5.0, 5.0)
        ],
        2: [Edge(2, 3, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(2, 1, 5.0, 5.0, 3.0)
        ],
        3: [Edge(3, 4, random.normalvariate(20, 1.5), 5.0, 3.0),
            Edge(3, 5, random.normalvariate(20, 1.5), 5.0, 6.0)
        ],
        4: [Edge(4, 5, random.normalvariate(20, 1.5), 5.0, 3.0),
            # Edge(4, 3, random.normalvariate(20, 1.5), 5.0)
        ],
        5: [],
    }
    return nodes, roads


def get_mid_graph():
    nodes=list(range(12))  # Example crossroads
    sources = [0, 6]
    sinks = [5, 11]
    roads = {
        0: [Edge(0, 1, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(0, 2, random.normalvariate(20, 1.5), 5.0, 5.0),
        ],
        1: [
            # Edge(1, 2, random.normalvariate(20, 1.5), 5.0),
            Edge(1, 3, random.normalvariate(20, 1.5), 5.0, 5.0)
        ],
        2: [Edge(2, 3, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(2, 1, 5.0, 5.0, 3.0),
            Edge(2, 8, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(2, 4, random.normalvariate(20, 1.5), 5.0, 10.0),
        ],
        3: [Edge(3, 4, random.normalvariate(20, 1.5), 5.0, 3.0),
            Edge(3, 5, random.normalvariate(20, 1.5), 5.0, 6.0),
            Edge(3, 2, random.normalvariate(20, 1.5), 5.0, 6.0)
        ],
        4: [Edge(4, 5, random.normalvariate(20, 1.5), 5.0, 3.0),
        ],
        5: [],

        6: [
            Edge(6, 7, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(6, 8, random.normalvariate(20, 1.5), 5.0, 10.0),
        ],
        7: [
            Edge(7, 9, random.normalvariate(20, 1.5), 5.0, 5.0),
            Edge(7, 8, random.normalvariate(20, 1.5), 5.0, 5.0)
        ],
        8: [Edge(8, 9, random.normalvariate(20, 1.5), 5.0, 10.0),
            Edge(8, 7, 5.0, 5.0, 3.0)
        ],
        9: [Edge(9, 10, random.normalvariate(20, 1.5), 5.0, 3.0),
            Edge(9, 11, random.normalvariate(20, 1.5), 5.0, 6.0)
        ],
        10: [Edge(10, 11, random.normalvariate(20, 1.5), 5.0, 3.0),
            Edge(10, 4, random.normalvariate(20, 1.5), 5.0, 3.0),
        ],
        11: [],
    }
    return nodes, roads, sources, sinks