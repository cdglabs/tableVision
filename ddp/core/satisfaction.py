import networkx as nx
import core.topology as topology


def is_horizontal_line((x1, y1), (x2, y2)):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    return dx > dy


def horizontal_subgraph(graph):
    return nx.Graph([
        (p1, p2)
        for (p1, p2) in graph.edges()
        if is_horizontal_line(p1, p2)
    ])


def vertical_subgraph(graph):
    return nx.Graph([
        (p1, p2)
        for (p1, p2) in graph.edges()
        if not is_horizontal_line(p1, p2)
    ])


def align_horizontal(graph):
    relabel = {}
    horizontal = horizontal_subgraph(graph)
    components = nx.connected_components(horizontal)
    for component in components:
        averageY = 0
        for (x, y) in component:
            averageY = averageY + y
        averageY = averageY / len(component)
        for (x, y) in component:
            relabel[(x, y)] = (x, averageY)
    return nx.relabel_nodes(graph, relabel)


def align_vertical(graph):
    relabel = {}
    vertical = vertical_subgraph(graph)
    components = nx.connected_components(vertical)
    for component in components:
        averageX = 0
        for (x, y) in component:
            averageX = averageX + x
        averageX = averageX / len(component)
        for (x, y) in component:
            relabel[(x, y)] = (averageX, y)
    return nx.relabel_nodes(graph, relabel)


def align(graph):
    return align_vertical(align_horizontal(graph))


def apply_same_length_constraint(graph):
    same_length_dict = {}
    for edge in graph.edges():
        edge_attr = graph.get_edge_data(*edge)
        if "same_length_strokes" in edge_attr:
            stroke_through_count = edge_attr["same_length_strokes"]
            if stroke_through_count > 0:
                if stroke_through_count in same_length_dict:
                    same_length_dict[stroke_through_count].append(edge)
                else:
                    same_length_dict[stroke_through_count] = [edge]
    
    print same_length_dict
    relabel = {}
    for edges_of_same_length in same_length_dict.values():
        average_length = 0
        for (n1, n2) in edges_of_same_length:
            average_length += topology.distance(n1, n2)
        average_length /= len(edges_of_same_length)
        
        print average_length
        
        # edges_of_same_length = ""
        
        # for ((n1x, n1y), (n2x, n2y)) in edges_of_same_length:
        #     relabel[(n1x, n1y)] = (averageX, y)
        #     relabel[(n1x, n1y)] = (averageX, y)
    
        # nx.relabel_nodes(graph, relabel)