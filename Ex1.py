import folium
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


M = np.array([
    [0, 1, 1, 1, 1],
    [0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0],
    [0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0]
])

matrix_dimension = [5, 5]

# 1/ Create and represent the graph corresponding to M
""" Solution 1 : suboptimal as it works only for small matrices and graphs """

edgelist = [("a", "b"), ("a", "c"), ("a", "d"), ("a", "e"),
            ("b", "c"), ("b", "d"), ("b", "e"),
            ("d", "b"), ("d", "c"), ("d", "e"),
            ("e", "a"), ("e", "c")]

G1 = nx.DiGraph(edgelist)
print("G1 : ", G1)


""" Solution 2 : only the nodes names are needed """

nodelist = ["a", "b", "c", "d", "e"]

G2 = nx.DiGraph()

for line in range(matrix_dimension[0]):
    for col in range(matrix_dimension[1]):
        if M[line][col] == 1:
            G2.add_edge(nodelist[line], nodelist[col])

print("G2 : ", G2)

"""Solution 3 : networkx built-in function (probably the most optimal)"""

G3 = nx.from_numpy_array(M, create_using=nx.DiGraph)
print("G3 : ", G3)

node_labels = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e"}
nx.relabel_nodes(G3, node_labels, copy=False)

#nx.draw_networkx(G3)
#plt.show()

# 1/ (b) Is the graph eulerian ?
""" A related digraph is eulerian if :
- for every vertex in V except start (v0) and finish (v1), d-(v) = d+(v)
- d+ (v0) = d- (v0 +1)
- d- (v1) = d+ (v1 +1) """

# 1/ (d) Determine the degree of each node and give it a meaningful representation
""" First (suboptimal) solution """
outgoing_half_degrees = []
ingoing_half_degrees = []

for v0 in range(matrix_dimension[0]):
    half_degree = []
    for v1 in range(matrix_dimension[1]):
        if M[v0][v1] == 1:
            half_degree.append(1)
    outgoing_half_degrees.append(sum(half_degree))

print("outgoing half-degrees : ", outgoing_half_degrees)

for v1 in range(matrix_dimension[1]):
    half_degree = []
    for v0 in range(matrix_dimension[0]):
        if M[v0][v1] == 1:
            half_degree.append(1)
    ingoing_half_degrees.append(sum(half_degree))

print("ingoing half-degrees : ", ingoing_half_degrees)

""" Second solution """

ingoing_half_degrees_2 = np.sum(M, axis=1).tolist()
outgoing_half_degrees_2 = np.sum(M, axis=0).tolist()

nodes_degrees = np.add(ingoing_half_degrees_2, outgoing_half_degrees_2)
print("nodes degrees : ", nodes_degrees)

"""degree_centrality(G)[source]"""

""" Thus, as half-degrees are not the same for every node except v0 and v1, our digraph is not eulerian. """

node_labels = {"a": "d(a)=5", "b": "d(b)=5", "c": "d(c)=4", "d": "d(d)=5", "e": "d(e)=5"}
nx.relabel_nodes(G3, node_labels, copy=False)
nx.draw_networkx(G3, node_size=[v * 400 for v in nodes_degrees])
plt.show()

