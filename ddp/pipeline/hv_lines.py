import infrastructure.intake as intake
import infrastructure.log as log

import core.topology as topology
import core.satisfaction as satisfaction


def run(graph):
    graph = topology.simplify_junctures(graph, 5)
    log.image(
        width=1100, height=800,
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )

    graph = topology.simplify_paths(graph, 3)
    log.image(
        width=1100, height=800,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = topology.hv_lines(graph)
    log.image(
        width=1100, height=800,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = satisfaction.align(graph)
    log.image(
        width=1100, height=800,
        points=graph.nodes(),
        lines=graph.edges()
    )

    return graph


def sample():
    return intake.gpickle("input/grid_graph.gpickle")
