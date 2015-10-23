import infrastructure.intake as intake
import infrastructure.log as log

import core.satisfaction as satisfaction


def run(graph):
    print graph

    graph = satisfaction.align(graph)
    log.image(
        width=1100,
        height=800,
        points=graph.nodes(),
        lines=graph.edges()
    )

    log.gpickle(graph)

    return graph


def sample():
    return intake.gpickle("input/grid_graph.gpickle")
