import infrastructure.intake as intake
import infrastructure.log as log

import core.topology as topology


def run(img):
    graph = topology.produce_graph(img)
    log.image(
        background=img,
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )

    graph = topology.simplify_junctures(graph, 5)
    log.image(
        background=img,
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )

    graph = topology.simplify_paths(graph, 3)
    log.image(
        background=img,
        points=graph.nodes(),
        lines=graph.edges()
    )

    graph = topology.straighten_lines(graph, 3.1416 * .1)
    log.image(
        background=img,
        points=graph.nodes(),
        lines=graph.edges()
    )

    log.gpickle(graph)

    return graph


def sample():
    return intake.image_file("input/grid_skeleton.png", gray=True)
