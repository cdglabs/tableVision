import networkx as nx
import core.topology as topology
from slvs import *
import core.util.vec as vec

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


def set_up_2d_workplane():
    # TODO 150 ... arbitrary system size
    sys = System(150)
    # First, we create our workplane. Its origin corresponds to the origin
    # of our base frame (x y z) = (0 0 0)
    p1 = Point3d(Param(0.0), Param(0.0), Param(0.0), sys)
    # and it is parallel to the xy plane, so it has basis vectors (1 0 0)
    # and (0 1 0).
    #Slvs_MakeQuaternion(1, 0, 0,
    #                    0, 1, 0, &qw, &qx, &qy, &qz);
    qw, qx, qy, qz = Slvs_MakeQuaternion(1, 0, 0,
                                         0, 1, 0)
    wnormal = Normal3d(Param(qw), Param(qx), Param(qy), Param(qz), sys)
    wplane = Workplane(p1, wnormal)
    # Now create a second group. We'll solve group 2, while leaving group 1
    # constant; so the workplane that we've created will be locked down,
    # and the solver can't move it.
    sys.default_group = 2
    return sys, wplane, wnormal



def print_slvs_result(sys):
    if sys.result == SLVS_RESULT_OKAY:
        print "OKAY"
    if sys.result == SLVS_RESULT_DIDNT_CONVERGE:
        print "DIDNT_CONVERGE"
    if sys.result == SLVS_RESULT_INCONSISTENT:
        print "INCONSISTENT"
    if sys.result == SLVS_RESULT_TOO_MANY_UNKNOWNS:
        print "TOO_MANY_UNKNOWNS"


def convert_graph_into_system(g):
    import networkx as nx
    sys, workplane, wnormal = set_up_2d_workplane()
    points = []
    for node in g.nodes():
        newPoint = Point2d(workplane, Param(node[0]), Param(node[1]))
        g.node[node]["solve"] = newPoint
        points.append(newPoint)
        # print "added point to graph"
    
    
    for edge in g.edges():
        # print "added edge to graph"
        pA = g.node[edge[0]]["solve"]
        pB = g.node[edge[1]]["solve"]
        line = LineSegment2d(workplane, pA, pB)
        data = g.get_edge_data(*edge)
        data["solve"] = line
        if "constrain" in data:
            if data["constrain"] == "horizontal":
                Constraint.horizontal(workplane, line)
            if data["constrain"] == "vertical":
                Constraint.vertical(workplane, line)
        if "length" not in data:
            dist = vec.distance(pA.to_openscad(), pB.to_openscad())
            # Constraint.distance(dist, workplane, pA, pB)
            # print "added normal dist constraint", dist
            pass
        else:
            print "set length of an edge", data["length"]
            Constraint.distance(data["length"], workplane, pA, pB)
        
        if True:
            print edge
            if vec.is_horizontal(*edge):
                print "horizontal"
                Constraint.horizontal(workplane, line)
            else:
                print "vertical"
                Constraint.vertical(workplane, line)
    
    
    print "trying to solve"
    result = sys.solve()
    print_slvs_result(sys)
    
    for node in g.nodes():
        point = g.node[node]["solve"]
        pArr = point.to_openscad()
        nx.relabel_nodes(g, {node: (pArr[0], pArr[1])}, copy=False)
    
    return g


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
            average_length += vec.distance(n1, n2)
        average_length /= len(edges_of_same_length)
        
        for edge in edges_of_same_length:
            graph.get_edge_data(*edge)["length"] = average_length
    
    
    
    graph = convert_graph_into_system(graph)
    return graph