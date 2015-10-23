import infrastructure.intake as intake
import infrastructure.log as log

import core.vision as vision
import core.topology as topology


def run(img):
    ink = vision.binarize_ink(img)
    log.image(background=ink)

    skeleton = vision.skeletonize(ink)
    log.image(background=skeleton)

    graph = topology.produce_graph(skeleton)
    log.image(
        background=skeleton,
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )
    log.gpickle(graph)

    return graph


def sample():
    return intake.image_file("input/grid_paper.png")
