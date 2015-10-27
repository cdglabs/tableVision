import networkx as nx

import infrastructure.intake as intake
import infrastructure.log as log
import infrastructure.printer as printer

import core.topology as topology
import core.satisfaction as satisfaction

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph


def run(img):
    img = extract_paper(img)

    graph = sketch_graph(img)

    components = nx.connected_components(graph)

    circles = [
        topology.fit_circle_to_points(list(component))
        for component in components
    ]

    log.image(img, circles=circles)

    svg = printer.circles_to_svg(circles)
    printer.write_file("log/out.svg", svg)
    pdf = printer.svg_to_pdf("log/out.svg", "log/out.pdf")
    printer.write_file("log/out.pdf", pdf)
    # printer.print_pdf("log/out.pdf")

    return graph


def sample():
    return intake.image_file("input/circle_test2.jpg")
