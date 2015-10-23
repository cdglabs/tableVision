import networkx as nx


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

