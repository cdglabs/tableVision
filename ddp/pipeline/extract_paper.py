import infrastructure.intake as intake
import infrastructure.log as log

import core.vision as vision


def run(img, logOn=True):
    edges = vision.find_edges(img)
    if logOn: log.image(background=edges)

    paper_contour = vision.find_paper(edges)
    if logOn: log.image(background=img, contours=[paper_contour])

    extracted = vision.extract_paper(img, paper_contour)
    if logOn: log.image(background=extracted)
    
    return extracted


def sample():
    return intake.image_file("input/grid_drawing.jpg")
