import networkx as nx

import infrastructure.intake as intake
import infrastructure.log as log

import core.topology as topology
import core.corner_detection as corner_detection

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph


def run(img):
    img = extract_paper(img)

    graph = sketch_graph(img)

    graph = topology.simplify_junctures(graph)
    log.hsvOrGreyImage(
        img,
        pixels=graph.nodes(),
        points=(node for node in graph.nodes() if graph.degree(node) != 2)
    )

    paths = topology.find_paths(graph)

    corners = []
    for path in paths:
        corners.extend(corner_detection.find_corners(path))

    log.hsvOrGreyImage(
        img,
        points=corners
    )

    return graph


def sample():
    return intake.image_file("input/curves.jpg")
