import infrastructure.intake as intake
import infrastructure.log as log
import infrastructure.printer as printer

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph
from pipeline.hv_lines import run as hv_lines


def run(img):
    img = extract_paper(img)
    graph = sketch_graph(img)
    graph = hv_lines(graph)

    log.image(
        background=img,
        points=graph.nodes(),
        lines=graph.edges()
    )

    svg = printer.graph_to_svg(graph)
    # printer.write_file("log/out.svg", svg)
    # printer.svg_to_pdf("log/out.svg", "log/out.pdf")
    # printer.print_pdf("log/out.pdf")


def sample():
    return intake.image_file("input/grid_drawing.jpg")
