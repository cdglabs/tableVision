"""
Functions for creating a graph from a skeletonized image (produce_graph) and
for simplifying graphs in various ways.

Graphs are NetworkX graphs where nodes are points, represented as (x,y) pairs.

Some vocabulary:

A juncture is a node with less than 2 or more than 2 edges.

A bridge is a node with exactly 2 edges.

A clump is a set of junctures that are all close to each other.

A path is a list of nodes, each one connects to the next.

"""


import networkx as nx
import math
import numpy as np

# TODO: This should be moved to util or Settings, etc.
import infrastructure.helper as helper


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


def produce_graph(skeleton_img, hsv_image = None):
    """Takes in a skeletonized image (with foreground as 255 and background as
    0) and produces a graph of appropriately connected pixel locations.
    """
    graph = nx.Graph()
    (rows, cols) = skeleton_img.shape
    for y in xrange(rows):
        for x in xrange(cols):
            pixel = skeleton_img.item(y, x)
            if pixel == 255:
                point = (x, y)
                attribute_dict = None
                if hsv_image is not None:
                    hsv_pixel = tuple( hsv_image[y][x] )
                    color = helper.Colors.get_color_compartment(hsv_pixel)
                    attribute_dict = {'color': color}
                graph.add_node(point, attribute_dict)

                for neighbor in neighbor_coords(point, (cols, rows)):
                    neighbor_pixel = skeleton_img.item(neighbor[1], neighbor[0])
                    if neighbor_pixel == 255:
                        graph.add_edge(point, neighbor)
    return graph


def find_junctures(graph):
    return find_nodes_with_degree(graph, lambda degree: degree != 2)


def find_termination_junctures(graph):
    return find_nodes_with_degree(graph, lambda degree: degree == 1)


def find_nodes_with_degree(graph, filter_function):
    junctures = []
    for node in nx.nodes_iter(graph):
        degree = nx.degree(graph, node)
        if filter_function(degree):
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


def get_path_color(graph, path):
    color_occurrence = {}
    for node in path:
        if 'color' in graph.node[node]:
            color = graph.node[node]['color']
            if color not in color_occurrence:
                color_occurrence[color] = 1
            else:
                color_occurrence[color] += 1

    if len(color_occurrence) == 0:
        return helper.Colors.Black
    return max(color_occurrence)


def find_same_length_constraints(graph):
    # find_paths from t-junctions!
    termination_junctures = find_termination_junctures(graph)
    paths_from_t_junctures = find_paths_from_junctures(graph, termination_junctures)

    constraint_junctions = []
    for (p1, p2) in itertools.combinations(paths_from_t_junctures, 2):
        last_node_p1 = p1[len(p1)-1]
        last_node_p2 = p2[len(p2)-1]
        path_end_degree = nx.degree(graph, last_node_p1)
        color_p1 = get_path_color(graph, p1)
        color_p2 = get_path_color(graph, p2)
        if last_node_p1 == last_node_p2 and color_p1 == color_p2 and path_end_degree == 4:
            print "found same length constraint!"
            constraint_junctions.append(last_node_p1)
            graph.node[last_node_p1]["constraint"] = "same_length"

    mygraph = nx.Graph()
    for path in paths_from_t_junctures:
        path_color = get_path_color(graph, path)
        start = path[0]
        end = path[len(path)-1]
        mygraph.add_node(start, {'color': path_color})
        mygraph.add_node(end, {'color': path_color})
        mygraph.add_edge(start, end, {'color': path_color})

        if path_color != helper.Colors.Black:
            for i in range(len(path)):
                # do not delete path end juncture if it implements a constraint
                node = path[i]
                if i != len(path)-1 and "constraint" not in graph.node[node]:
                    graph.remove_node(node)
                else:
                    print "left constraint juncture in place"

    return mygraph, constraint_junctions



def simplify_junctures(graph, epsilon=5):
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
    return find_paths_from_junctures(graph, find_junctures(graph))


def find_paths_from_junctures(graph, junctures):
    """Returns a list of paths between junctures. Each path is a list of
    nodes. The first and last node in the path is a juncture, and each
    intermediate node in the path is a bridge.
    """

    # TODO: This should also find cyclical paths, that is circular paths which
    # are not connected to any junctures. Or perhaps there should be a
    # separate function for finding cyclical paths.

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


def simplify_paths(graph, epsilon=3):
    """Finds all paths and simplifies them using the RDP algorithm for
    reducing the number of points on a curve. All remaining nodes will be
    within epsilon of the original curve."""

    # TODO: Should also simplify cyclical paths. See find_paths. But RDP needs
    # endpoints. A robust way to deal with cycles might be to use the potrace
    # algorithm instead of RDP.

    # http://potrace.sourceforge.net/potrace.pdf

    graph = graph.copy()
    paths = find_paths(graph)
    for path in paths:
        simplified_path = rdp(path, epsilon)
        # Delete original path.
        edge_attributes = {"same_length_strokes": 0}
        for index, node in enumerate(path):
            if "constraint" in graph.node[node] and graph.node[node]["constraint"] == "same_length":
                edge_attributes["same_length_strokes"] += 1
                print "added strokes", edge_attributes["same_length_strokes"]

            if index == 0 or index == len(path)-1:
                continue
            graph.remove_node(node)
        for (a, b) in pairwise(simplified_path):
            graph.add_edge(a, b, edge_attributes)
    return graph


def is_horizontal((x1,y1), (x2,y2)):
    """Returns True if points are more horizontal to each other than vertical
    to each other."""
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return dx > dy

def get_bridge_ends(graph, node):
    """Returns the nodes on either side of a bridge (a node with 2 edges)."""
    neighbors = list(nx.all_neighbors(graph, node))
    p1 = neighbors[0]
    p2 = neighbors[1]
    return (p1, p2)


def merge_attributes(dict1, dict2):
    for key in dict2:
        if key in dict1:
            dict1[key] += dict2[key]
        else:
            dict1[key] = dict2[key]
    return dict1


def remove_bridge(graph, node):
    """Mutates graph. Assumes node is a bridge (has 2 edges). Removes bridge
    node and connects either side of the bridge to each other."""
    (p1, p2) = get_bridge_ends(graph, node)
    # preserve constraints from old edges to new edge
    edge1attributes = graph.get_edge_data(p1, node)
    edge2attributes = graph.get_edge_data(p2, node)

    graph.remove_node(node)
    graph.add_edge(p1, p2, merge_attributes(edge1attributes, edge2attributes))


def hv_lines(graph):
    """Removes any nodes of two edges that are redundant assuming the graph
    only represents horizontal and vertical lines."""

    graph = graph.copy()
    to_delete = set([])
    for node in graph.nodes_iter():
        if graph.degree(node) == 2:
            (p1, p2) = get_bridge_ends(graph, node)
            if is_horizontal(p1, node) == is_horizontal(node, p2):
                to_delete.add(node)
    for node in to_delete:
        remove_bridge(graph, node)
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
            (p1, p2) = get_bridge_ends(graph, node)
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
        remove_bridge(graph, node)
    return graph




