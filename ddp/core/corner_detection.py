"""
These algorithms are concerned with finding corners in a path. A path is a
list of (x,y) points.

They return a list of corners which does not include the endpoints of the
path.

There are different criteria depending on the color/type of the line for
finding corners. For example, we can be stricter about finding corners in hv
lines than we can in ordinary straight lines. Thus this module has several
algorithms for finding corners.
"""

import math
import core.util.vec as vec
import core.util.stepping as stepping
import core.topology as topology



def find_corners_hv(path, epsilon=3):
    corners = []
    simplified_path = fit.rdp(path, epsilon)
    for (a, b, c) in stepping.triplewise(simplified_path):
        if vec.is_horizontal(a, b) != vec.is_horizontal(b, c):
            corners.append(b)
    return corners


def get_neighborhood(path, index, direction, neighborhood):
    """Finds the neighborhood of points around path[index].

    That is, all the points that are within neighborhood distance (measured as
    path length) from the point in question (path[index]). This includes the
    point itself.

    We look at the points on the path before the point (if direction is -1) or
    after the point (if direction is 1), and we return the points that are
    within neighborhood distance of the point.
    """
    path_length = 0
    result = [path[index]]
    index += direction
    while 0 <= index < len(path):
        point = path[index]
        prev_point = path[index - direction]
        step_distance = vec.distance(prev_point, point)
        path_length += step_distance
        if path_length > neighborhood:
            break
        result.append(point)
        index += direction
    return result


def get_tangent_direction(path, index, direction, neighborhood):
    """The tangent as normalized vector at the point at path[index].

    This is determined by considering the points leading either into the point
    (if direction is -1) or out of the point (if direction is 1).

    We look at the points that are within the neighborhood of the point in
    question. We fit a circle to these points and then get the tangent of the
    circle at the point.
    """
    origin = path[index]
    points = get_neighborhood(path, index, direction, neighborhood)

    if is_colinear(points):
        # If they're colinear, then getting the tangent is easy. We just pick
        # two points in the path to get the direction.
        return vec.normalize(vec.sub(origin, points[1]))

    (center, radius) = topology.fit_circle_to_points(points)
    perpendicular = vec.normalize(vec.sub(center, origin))
    (px, py) = perpendicular
    # There are two options for tangent direction: a or b.
    a = (-py, px)
    b = (py, -px)
    pa = vec.add(origin, a)
    pb = vec.add(origin, b)
    # We choose the one that is furthest from points.
    a_total = 0
    b_total = 0
    for point in points:
        a_total += vec.quadrance(pa, point)
        b_total += vec.quadrance(pb, point)
    if a_total > b_total:
        return a
    else:
        return b


def corner_score(path, index, neighborhood):
    """The likelihood that the point at index along the path is a corner.

    It is computed by determining the tangent vector coming in to the point
    and the tangent vector coming out of the point, and then getting the angle
    between these two vectors.

    The corner score is the difference between pi (180 degrees) and this
    angle. The higher the score, the more likely the point is a sharp corner.
    """
    if index < 10 or index >= len(path) - 10:
        # If there are fewer than 10 points before or after the point, we don't
        # have good enough information to tell that it's a corner, so we
        # return a corner score of 0.
        return 0
    before_tangent = get_tangent_direction(path, index, -1, neighborhood)
    after_tangent = get_tangent_direction(path, index, 1, neighborhood)
    a = angle(before_tangent, (0,0), after_tangent)
    return math.pi - a


def extremeness_score(path, index, neighborhood):
    """How extreme is the point at path[index].

    This is computed by looking at the neighborhood of points and seeing how
    towards-one-side these points are.

    The higher the score, the more extreme is the point in question.
    """
    origin = path[index]

    before_points = get_neighborhood(path, index, -1, neighborhood)
    after_points = get_neighborhood(path, index, 1, neighborhood)

    # Ensure that before_points and after_points have the same number of
    # points, otherwise the score will get skewed towards whichever side has
    # more points!
    length = min(len(before_points), len(after_points))
    before_points = before_points[0:length]
    after_points = after_points[0:length]

    total = (0,0)
    for point in before_points + after_points:
        d = vec.sub(point, origin)
        if not (d[0] == 0 and d[1] == 0):
            total = vec.add(total, vec.normalize(d))

    (x,y) = total
    return x**2 + y**2


def find_corners(path, neighborhood=22, angle_tolerance=math.pi/5):
    corners = []

    # for (index, point) in enumerate(path):
    #     if corner_score(path, index, neighborhood) > angle_tolerance:
    #         corners.append(point)
    # return corners

    corner_scores = []
    extremeness_scores = []
    for (index, point) in enumerate(path):
        c = corner_score(path, index, neighborhood)
        corner_scores.append(c)
        if c > angle_tolerance:
            e = extremeness_score(path, index, neighborhood)
            extremeness_scores.append(e)
        else:
            extremeness_scores.append(0)

    for (index, score) in enumerate(corner_scores):
        if score > angle_tolerance:
            # To count as a corner, the point's extremeness score needs to be
            # the highest in its neighborhood.
            before_points = get_neighborhood(path, index, -1, neighborhood)
            after_points = get_neighborhood(path, index, 1, neighborhood)
            start_index = index - len(before_points) + 1
            end_index = index + len(after_points) - 1

            extremeness = extremeness_scores[index]
            is_highest = True
            for neighbor_index in range(start_index, end_index+1):
                neighbor_extremeness = extremeness_scores[neighbor_index]
                if neighbor_extremeness > extremeness:
                    is_highest = False
                    break
                if neighbor_extremeness == extremeness and neighbor_index < index:
                    # We tie break in favor of the earlier corner.
                    is_highest = False
                    break
            if is_highest:
                corners.append(path[index])

    return corners






