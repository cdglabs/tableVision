"""
Utitily functions for working with 2D vectors.

Vectors are represented as pairs of numbers.
"""

import math


def add((x1,y1), (x2,y2)):
    return ((x1+x2), (y1+y2))


def sub((x1,y1), (x2,y2)):
    return ((x1-x2), (y1-y2))


def dot((x1,y1), (x2,y2)):
    return x1*x2 + y1*y2


def length((x,y)):
    return math.sqrt(x**2 + y**2)


def normalize((x,y)):
    l = length((x,y))
    return (x/l, y/l)


def quadrance(p1, p2):
    """Distance-squared between two points."""
    return length(sub(p2, p1))


def distance(p1, p2):
    return math.sqrt(quadrance(p1, p2))


def point_line_distance(point, start, end):
    """Distance from point to the line defined by start and end"""
    if (start == end):
        return distance(point, start)
    else:
        n = abs(
            (end[0] - start[0]) * (start[1] - point[1]) -
            (start[0] - point[0]) * (end[1] - start[1])
        )
        d = math.sqrt(
            (end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2
        )
        return n / d


def angle(a, b, c):
    """Returns the angle (in radians) created between 3 points. The angle at B
    going from A to C. Returned angle is always between 0 and pi.
    """
    ab = distance(a, b)
    bc = distance(b, c)
    ac = distance(a, c)
    d = (ab**2 + bc**2 - ac**2) / (2 * ab * bc)
    d = min(1, max(d, -1))
    return math.acos(d)


def colinear3((a,b), (m,n), (x,y)):
    """Returns whether 3 points are colinear."""
    # via http://math.stackexchange.com/questions/405966/if-i-have-three-points-is-there-an-easy-way-to-tell-if-they-are-collinear
    det = a*(n-y) + m*(y-b) + x*(b-n)
    return det == 0


def colinear(points):
    """Returns whether a list of points are colinear."""
    if len(points) < 3:
        return True

    p1 = points[0]
    p2 = points[1]
    for point in points:
        if not colinear3(p1, p2, point):
            return False
    return True


def is_horizontal(p1, p2):
    """Returns True if the line from p1 to p2 is more horizontal than it is
    vertical."""
    (dx, dy) = sub(p2, p1)
    return dx > dy

