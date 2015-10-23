import infrastructure.intake as intake
import infrastructure.log as log

import core.vision as vision


def run(img):
    edges = vision.find_edges(img)
    log.image(background=edges)

    paper_contour = vision.find_paper(edges)
    log.image(background=img, contours=[paper_contour])

    extracted = vision.extract_paper(img, paper_contour)
    log.image(background=extracted)

    ink = vision.binarize_ink(extracted)
    log.image(background=ink)

    skeleton = vision.skeletonize(ink)
    log.image(background=skeleton)

    return skeleton


def sample():
    return intake.image_file("input/grid_drawing.jpg")
