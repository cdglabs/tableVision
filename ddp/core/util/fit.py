"""Functions for fitting shapes to data points."""

import numpy as np
import core.util.vec as vec


def rdp(points, epsilon):
    """Reduces a series of points to a simplified version that loses detail, but
    maintains the general shape of the series.

    The Ramer-Douglas-Peucker algorithm roughly ported from the pseudo-code
    provided by http://en.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm

    via https://github.com/sebleier/RDP/
    """
    dmax = 0.0
    index = 0
    for i in range(1, len(points) - 1):
        d = vec.point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d
    if dmax >= epsilon:
        results = rdp(points[:index+1], epsilon)[:-1] + \
            rdp(points[index:], epsilon)
    else:
        results = [points[0], points[-1]]
    return results


def plane_to_points(points):
    """Takes a list of 3D data points [(x,y,z)] and fits a plane. Returns
    (center, normal) as numpy arrays.

    via https://gist.github.com/lambdalisue/7201028
    """
    points = np.array(points)
    center = np.average(points, axis=0)
    # Normalize points as vector from center.
    points = points - center
    # Singular value decomposition
    U, S, V = np.linalg.svd(points)
    # The last row of V matrix indicate the eigenvectors of smallest
    # eigenvalues (singular values).
    normal = V[-1]
    return (center, normal)


def intersect_plane_with_paraboloid(center, normal):
    """Intersects a plane given as (center, normal) with the paraboloid z =
    x**2 + y**2. Then projects this ellipse onto the x-y plane giving a
    circle. This circle is returned as (center, radius).

    We know the equation of the plane:

        a*x + b*y + c*z = d

    We know for any point on the plane p,

        normal dot (p - center) = 0

    Our equation for the paraboloid is:

        x**2 + y**2 = z

    Substituting for z using our equation for the plane,

        x**2 + y**2 = (d - a*x - b*y) / c

    Rearranging x and y to the lhs,

        x**2 + (a/c)*x + y**2 + (b/c)*y = d/c

    Recall that a circle of radius r centered at (x0, y0) has equation:

        (x - x0)**2 + (y - y0)**2 = r**2

        x**2 - 2*x0*x + x0**2 + y**2 - 2*y0*y + y0**2 = r**2

        x**2 - 2*x0*x + y**2 - 2*y0*y = r**2 - x0**2 - y0**2

    So we know that:

        a/c = -2*x0

        b/c = -2*y0

        d/c = r**2 - x0**2 - y0**2

    """
    (a, b, c) = normal
    d = np.dot(normal, center)

    x0 = -(a / c) / 2
    y0 = -(b / c) / 2
    r = np.sqrt( (d / c) + x0**2 + y0**2)

    return ((x0,y0), r)


def circle_to_points(points):
    """Takes a list of 2D data points [(x,y)] and fits a circle. Returns
    (center, radius).
    """

    points = np.array(points)
    p0 = points[0]
    # Normalize points as vector from p0.
    points = points - p0
    # Now we project onto the parabola z = x**2 + y**2.
    z = np.sum(points**2, axis=1)
    points = np.c_[points, z]
    (plane_center, plane_normal) = plane_to_points(points)

    (center, radius) = intersect_plane_with_paraboloid(plane_center, plane_normal)

    # Unnormalize from p0.
    center = center + p0

    return (center, radius)





