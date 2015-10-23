import numpy as np
import cv2

from source import network
from source import constrain
from output import printer

from source.find_edges import *
from source.find_paper import *
from source.extract_paper import *
from source.white_balance import *
from source.binarize_ink import *
from source.skeletonize import *


out_count = 0
def writeout(img):
  global out_count
  out_count = out_count + 1
  file_name = "output/out" + str(out_count) + ".png"
  cv2.imwrite(file_name, img)


img = cv2.imread("input/sample1.jpg")

edges = find_edges(img)
#~ writeout(find_edges_out(edges))

paper_contour = find_paper(edges)
#~ writeout(paper.find_paper_out(paper_contour, img))

extracted = extract_paper(img, paper_contour)
#~ writeout(paper.extract_paper_out(extracted))

ink = binarize_ink(extracted)
#~ writeout(paper.binarize_ink_out(ink))

skeleton = skeletonize(ink)
#~ writeout(paper.skeletonize_out(skeleton))


graph = network.produce_graph(skeleton)
writeout(network.produce_graph_out(graph, extracted))

graph = network.simplify_junctures(graph, 5)
writeout(network.simplify_junctures_out(graph, extracted))

graph = network.simplify_paths(graph, 3)
writeout(network.simplify_paths_out(graph, extracted))

graph = network.straighten_lines(graph, 3.1416 * .1)
writeout(network.straighten_lines_out(graph, extracted))



graph = constrain.align(graph)
writeout(constrain.align_out(graph, extracted))



svg = printer.graph_to_svg(graph)

printer.write_file("output/out.svg", svg)

#~ printer.svg_to_pdf("output/out.svg", "output/out.pdf")

#~ printer.print_pdf("output/out.pdf")


print "done"
