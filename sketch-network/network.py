import numpy as np
import cv2
from skimage import morphology
import networkx as nx
import itertools
from rdp import rdp
import math


# via https://docs.python.org/2/library/itertools.html
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

# Will find up to 8 neighbors of (x,y). You need to pass in img so that it
# knows the dimensions.
def neighbor_coords(img, (x,y) ):
  (rows, cols) = img.shape
  neighbors = []
  for i in [-1, 0, 1]:
    for j in [-1, 0, 1]:
      if i == 0 and j == 0:
        continue
      neighbor_x = x + i
      neighbor_y = y + j
      if 0 < neighbor_x < cols and 0 < neighbor_y < rows:
        neighbors.append( (neighbor_x,neighbor_y) )
  return neighbors

# Takes in a skeletonized image (with foreground as 255 and background as 0)
# and produces a graph of appropriately connected pixel locations.
def produce_graph(img):
  graph = nx.Graph()
  (rows, cols) = img.shape
  for y in xrange(rows):
    for x in xrange(cols):
      pixel = img.item(y, x)
      if pixel == 255:
        point = (x,y)
        graph.add_node(point)
        for neighbor in neighbor_coords(img, point):
          neighbor_pixel = img.item(neighbor[1], neighbor[0])
          if neighbor_pixel == 255:
            graph.add_edge(point, neighbor)
  return graph

# Takes a graph and returns all nodes that are "junctures", that is, have less
# than 2 or more than 2 edges.
def find_junctures(graph):
  junctures = []
  for node in nx.nodes_iter(graph):
    degree = nx.degree(graph, node)
    if degree != 2:
      junctures.append(node)
  return junctures

# Quadrance is distance squared.
def quadrance( (x1,y1) , (x2,y2) ):
  dx = x2 - x1
  dy = y2 - y1
  return dx*dx + dy*dy

# Takes a graph and a max_distance and returns a list of clumps. Each clump is
# a set of junctures which are within max_distance of each other.
def find_clumps(graph, max_distance):
  max_quadrance = max_distance * max_distance
  junctures = find_junctures(graph)
  clump_graph = nx.Graph()
  for juncture in junctures:
    clump_graph.add_node(juncture)
  for (i, j) in itertools.combinations(junctures, 2):
    if quadrance(i, j) < max_quadrance:
      clump_graph.add_edge(i, j)
  return nx.connected_components(clump_graph)

# Mutates graph. Replaces all clumps (see above) with a single juncture node.
# For each clump, any nodes within max_distance of the clump are deleted.
# Remaining nodes are connected back to the simplified junctures
# appropriately.
def simplify_junctures(graph, max_distance):
  max_quadrance = max_distance * max_distance
  clumps = find_clumps(graph, max_distance)

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

    clump_center = (0,0)
    for juncture in clump:
      clump_center = (clump_center[0]+juncture[0], clump_center[1]+juncture[1])
    clump_center = (clump_center[0] / len(clump), clump_center[1] / len(clump))

    for node in to_delete:
      graph.remove_node(node)

    graph.add_node(clump_center)
    for node in to_join:
      graph.add_edge(node, clump_center)

# Returns a list of paths which you can think of as the "bridges" in the
# graph. Each path is a list of nodes. The first and last node in the path is
# a juncture, and each intermediate node in the path has two neighbors.
def find_paths(graph):
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

# Finds all paths and simplifies them using the RDP algorithm for reducing the
# number of points on a curve. All remaining nodes will be within max_distance
# of the non-simplified curve.
def simplify_paths(graph, max_distance):
  paths = find_paths(graph)
  for path in paths:
    simplified_path = rdp(path, max_distance)
    # Delete original path.
    for index, node in enumerate(path):
      if index == 0 or index == len(path)-1:
        continue
      graph.remove_node(node)
    for (a, b) in pairwise(simplified_path):
      graph.add_edge(a, b)

# Removes any nodes of two edges that form an angle less than max_angle from
# pi radians. TODO: This could use cleanup.
def straighten_lines(graph, max_angle):
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



# Read in image
img = cv2.imread('sample1.png')
grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)



graph = produce_graph(grey)

out = img.copy()
for node in graph.nodes_iter():
  degree = nx.degree(graph, node)
  if degree != 2:
    cv2.circle(out, node, 4, (0,0,255), -1)
cv2.imwrite("out1.png", out)



simplify_junctures(graph, 5)

out = img.copy()
for node in graph.nodes_iter():
  degree = nx.degree(graph, node)
  if degree != 2:
    cv2.circle(out, node, 4, (0,0,255), -1)
cv2.imwrite("out2.png", out)


simplify_paths(graph, 3)

out = img.copy()
for (p1, p2) in graph.edges_iter():
  cv2.line(out, p1, p2, (0,255,0), 2)
for node in graph.nodes_iter():
  cv2.circle(out, node, 4, (0,0,255), -1)
cv2.imwrite("out3.png", out)



straighten_lines(graph, math.pi * .1)

out = img.copy()
for (p1, p2) in graph.edges_iter():
  cv2.line(out, p1, p2, (0,255,0), 2)
for node in graph.nodes_iter():
  cv2.circle(out, node, 4, (0,0,255), -1)
cv2.imwrite("out4.png", out)


