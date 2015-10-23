import numpy as np

import infrastructure.intake as intake
import infrastructure.log as log

import core.topology as topology
import core.satisfaction as satisfaction


def run(graph, background=None):
    if background is None:
        background = np.zeros((850,1100,3), np.uint8)

    graph = topology.simplify_junctures(graph)
    log.image(
        background=background,
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )

    graph = topology.simplify_paths(graph)
    log.image(
        background=background,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = topology.hv_lines(graph)
    log.image(
        background=background,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = satisfaction.align(graph)
    log.image(
        background=background,
        points=graph.nodes(),
        lines=graph.edges()
    )

    return graph


def sample():
    return intake.gpickle("input/grid_graph.gpickle")
