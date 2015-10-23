import networkx as nx
import itertools
import math


def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ...

    via https://docs.python.org/2/library/itertools.html
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)


def neighbor_coords((x,y), (width,height)):
    """Returns up to 8 pixel neighbor coordinates of (x,y)."""
    neighbors = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0:
                continue
            neighbor_x = x + i
            neighbor_y = y + j
            if 0 < neighbor_x < width and 0 < neighbor_y < height:
                neighbors.append((neighbor_x, neighbor_y))
    return neighbors


def quadrance((x1,y1), (x2,y2)):
    """Returns distance-squared between two points."""
    dx = x2 - x1
    dy = y2 - y1
    return dx*dx + dy*dy


def distance(p1, p2):
    return math.sqrt(quadrance(p1, p2))


def point_line_distance(point, start, end):
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
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d
    if dmax >= epsilon:
        results = rdp(points[:index+1], epsilon)[:-1] + \
            rdp(points[index:], epsilon)
    else:
        results = [points[0], points[-1]]
    return results


def produce_graph(img):
    """Takes in a skeletonized image (with foreground as 255 and background as
    0) and produces a graph of appropriately connected pixel locations.
    """
    graph = nx.Graph()
    (rows, cols) = img.shape
    for y in xrange(rows):
        for x in xrange(cols):
            pixel = img.item(y, x)
            if pixel == 255:
                point = (x, y)
                graph.add_node(point)
                for neighbor in neighbor_coords(point, (cols, rows)):
                    neighbor_pixel = img.item(neighbor[1], neighbor[0])
                    if neighbor_pixel == 255:
                        graph.add_edge(point, neighbor)
    return graph


def find_junctures(graph):
    """Returns all nodes that are "junctures", that is, have less than 2 or
    more than 2 edges.
    """
    junctures = []
    for node in nx.nodes_iter(graph):
        degree = nx.degree(graph, node)
        if degree != 2:
            junctures.append(node)
    return junctures


def find_clumps(graph, epsilon):
    """Returns a list of "clumps". Each clump is a set of junctures which are
    within epsilon of each other."""
    max_quadrance = epsilon * epsilon
    junctures = find_junctures(graph)
    clump_graph = nx.Graph()
    for juncture in junctures:
        clump_graph.add_node(juncture)
    for (i, j) in itertools.combinations(junctures, 2):
        if quadrance(i, j) < max_quadrance:
            clump_graph.add_edge(i, j)
    return nx.connected_components(clump_graph)


def simplify_junctures(graph, epsilon):
    """Simplifies clumps by replacing them with a single juncture node. For
    each clump, any nodes within epsilon of the clump are deleted. Remaining
    nodes are connected back to the simplified junctures appropriately."""
    graph = graph.copy()
    max_quadrance = epsilon * epsilon
    clumps = find_clumps(graph, epsilon)

    for clump in clumps:
        to_delete = set([])
        for node in graph.nodes_iter():
            for juncture in clump:
                if quadrance(node, juncture) < max_quadrance:
                    to_delete.add(node)

        to_join = set([])
        for node in to_delete:
            for neighbor in nx.all_neighbors(graph, node):
                if not (neighbor in to_delete):
                    to_join.add(neighbor)

        clump_center = (0, 0)
        for juncture in clump:
            clump_center = (
                clump_center[0]+juncture[0], clump_center[1]+juncture[1])
        clump_center = (
            clump_center[0] / len(clump), clump_center[1] / len(clump))

        for node in to_delete:
            graph.remove_node(node)

        for node in to_join:
            graph.add_edge(node, clump_center)

    return graph


def find_paths(graph):
    """Returns a list of paths which you can think of as the "bridges" in the
    graph. Each path is a list of nodes. The first and last node in the path
    is a juncture, and each intermediate node in the path has two neighbors.
    """

    # TODO: This should also find cyclical paths, that is circular paths which
    # are not connected to any junctures.

    junctures = find_junctures(graph)
    paths = []
    visited_nodes = set([])

    def follow_path(path, current_node, previous_node):
        path.append(current_node)
        visited_nodes.add(current_node)
        if nx.degree(graph, current_node) == 2:
            neighbors = list(nx.all_neighbors(graph, current_node))
            if neighbors[0] == previous_node:
                next_node = neighbors[1]
            else:
                next_node = neighbors[0]
            follow_path(path, next_node, current_node)

    for juncture in junctures:
        neighbors = nx.all_neighbors(graph, juncture)
        for neighbor in neighbors:
            if not (neighbor in visited_nodes):
                path = [juncture]
                follow_path(path, neighbor, juncture)
                paths.append(path)

    return paths


def simplify_paths(graph, epsilon):
    """Finds all paths and simplifies them using the RDP algorithm for
    reducing the number of points on a curve. All remaining nodes will be
    within epsilon of the original curve."""

    # TODO: Should also simplify cyclical paths. See find_paths. A robust way
    # to deal with cycles might be to use the potrace algorithm instead of
    # RDP.

    # http://potrace.sourceforge.net/potrace.pdf

    graph = graph.copy()
    paths = find_paths(graph)
    for path in paths:
        simplified_path = rdp(path, epsilon)
        # Delete original path.
        for index, node in enumerate(path):
            if index == 0 or index == len(path)-1:
                continue
            graph.remove_node(node)
        for (a, b) in pairwise(simplified_path):
            graph.add_edge(a, b)
    return graph


def straighten_lines(graph, max_angle):
    """Removes any nodes of two edges that form an angle less than max_angle
    from pi radians.
    """

    # TODO: This could use cleanup. The formulation of max_angle is awkward.

    graph = graph.copy()
    to_delete = set([])
    for node in graph.nodes_iter():
        if nx.degree(graph, node) == 2:
            neighbors = list(nx.all_neighbors(graph, node))
            p1 = neighbors[0]
            p2 = neighbors[1]
            a = math.sqrt(quadrance(p1, node))
            b = math.sqrt(quadrance(p2, node))
            c = math.sqrt(quadrance(p1, p2))
            if a + b == c:
                to_delete.add(node)
                continue
            angle = math.acos((c*c - a*a - b*b) / (2*a*b))
            if angle < max_angle:
                to_delete.add(node)
    for node in to_delete:
        neighbors = list(nx.all_neighbors(graph, node))
        p1 = neighbors[0]
        p2 = neighbors[1]
        graph.remove_node(node)
        graph.add_edge(p1, p2)
    return graph
