import infrastructure.intake as intake
import infrastructure.log as log
import infrastructure.printer as printer

from pipeline.cv import run as cv
from pipeline.to_graph import run as to_graph
from hv_lines import run as hv_lines


def run(img):
    skeleton = cv(img)
    graph = to_graph(skeleton)
    graph = hv_lines(graph)

    svg = printer.graph_to_svg(graph)

    printer.write_file("log/out.svg", svg)
    printer.svg_to_pdf("log/out.svg", "log/out.pdf")
    # printer.print_pdf("log/out.pdf")


def sample():
    return intake.image_file("input/grid_drawing.jpg")
