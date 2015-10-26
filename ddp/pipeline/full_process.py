import infrastructure.intake as intake
import infrastructure.printer as printer
import infrastructure.photoClient as photoClient

from pipeline.extract_paper import run as extract_paper
from pipeline.sketch_graph import run as sketch_graph
from pipeline.hv_lines import run as hv_lines


def run(img):
    extracted = extract_paper(img)
    graph = sketch_graph(extracted)
    graph = hv_lines(graph, background=extracted)

    svg = printer.graph_to_svg(graph)
    printer.write_file("log/out.svg", svg)
    pdf = printer.svg_to_pdf("log/out.svg", "log/out.pdf")
    printer.write_file("log/out.pdf", pdf)
    printer.print_pdf("log/out.pdf")


def sample():
    file = "input/grid_drawing.jpg"
    try:
        file = photoClient.get_photo_from_server()
    except Exception:
        print "could not get photo. taking default file."
        pass
    
    return intake.image_file(file)
