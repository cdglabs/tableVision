import infrastructure.intake as intake
import infrastructure.log as log

import core.vision as vision
import core.topology as topology


def run(img):
    img = vision.convert_hsv_image_to_greyscale_emphasising_saturation(img)
    ink = vision.binarize_ink_IMPROVED(img)
    log.bgrOrGreyImage(ink)

    skeleton = vision.skeletonize(ink)
    log.bgrOrGreyImage(skeleton)

    graph = topology.produce_graph(skeleton)
    log.hsvOrGreyImage(img,
        pixels=graph.nodes()
    )
    log.gpickle(graph)

    return graph


def sample():
    return intake.image_file("input/grid_paper.png")
