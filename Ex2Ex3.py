import branca.colormap
import folium
import geopy.distance
import json
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from folium import plugins
from geopy import distance
from scipy.spatial import distance

# Data import and merging into unique df
data1 = pd.read_json("rawData\\Copies\\planet_osm_point_202312122304_1_copy.json", orient="records", lines=True)
data2 = pd.read_json("rawData\\Copies\\planet_osm_point_202312122304_2_copy.json", orient="records", lines=True)
data3 = pd.read_json("rawData\\Copies\\planet_osm_point_202312122304_3_copy.json", orient="records", lines=True)
data4 = pd.read_json("rawData\\Copies\\planet_osm_point_202312122304_4_copy.json", orient="records", lines=True)

# print(data1.tail)
# print(data4.tail)
# print(data2.tail)
# print(data3.tail)

data = pd.concat([data1, data2, data3, data4])


# Clearing all tags not refering to furniture or urban landscape (columns) and the associated elements (rows)
removed_tags = ["osm_id", "access", "addr:housename", "sport", "bicycle", "public_transport", "addr:housenumber",
                "addr:interpolation", "admin_level", "area", "boundary", "brand", "capital", "construction", "covered",
                "cutting", "denomination", "disused", "ele",
                "embankment", "foot", "generator:source", "horse", "intermittent", "junction", "landuse", "layer",
                "man_made", "motorcar", "name", "natural", "operator", "population", "power_source", "ref", "width",
                "z_order"]

data.drop(labels=removed_tags, axis=1, inplace=True)
urban_df = data.dropna(axis=0, how="all", subset=data.columns.difference(['way']))
#print(urban_df)

# Pivoting data from columns categories to row categories
urban_categories = pd.Index.to_series(urban_df.columns)
non_null_values = []

for index, row in urban_df.iterrows():
    not_null_mask = pd.array(row.notna(), dtype="boolean")
    categories_list = urban_categories.loc[not_null_mask].values
    non_null_values.append(categories_list[0:-1])  # Avoids adding the "Way" column that isn't a category

urban_df.insert(0, "category", pd.Series(non_null_values))
points_by_category = urban_df[["way", "category"]].copy()
#print(points_by_category)


# Reformating "way" tag (lon/lat) into lat/lon
points_by_category["lon_lat_coord"] = points_by_category["way"].str[7:-1]
points_by_category[["longitude", "latitude"]] = points_by_category["lon_lat_coord"].str.split(" ", expand=True)
points_by_category.drop("lon_lat_coord", axis=1, inplace=True)

points_by_category["latitude"] = pd.to_numeric(points_by_category["latitude"], downcast="float")
points_by_category["longitude"] = pd.to_numeric(points_by_category["longitude"], downcast="float")
points_by_category.drop("way", axis=1, inplace=True)
#print(points_by_category)


# Reformating "category" column from array to entity and deleting empty categories
"""Note : took a shortcut with taking only the first entity of the list, but most of the entities that had two 
categories were "amenity" and "shop", which I decided to reduce to only "amenity" category"""

categories = points_by_category["category"].str[0]
points_by_category.drop("category", axis=1, inplace=True)
points_by_category.insert(0, "category", categories)
#print(points_by_category)

"""Empty categories: aerialway, bridge, culvert, lock, military, oneWay, route, toll, tunnel, water, wood"""


# Creating coordinates list to fit different function input
coordinate_list = []
for index, row in points_by_category.iterrows():
    coordinate_list.append((row["latitude"], row["longitude"]))


# Creating map
"""testmap = folium.Map(location=(47.8, 2.5))
for i in range(len(points_by_category)):
    folium.CircleMarker(location=coordinate_list[i], radius=1).add_to(testmap)

cluster = plugins.MarkerCluster(locations=coordinate_list, popups=points_by_category["category"].tolist())
testmap.add_child(cluster)
testmap.save("testmap.html")"""


# Creating graph
categories_count_df = points_by_category.groupby("category").size().reset_index(name="count")
nodes_size_list = [v for v in categories_count_df["count"]]
nodes_size_list_normalized = [x/max(nodes_size_list)*1000 for x in nodes_size_list]

G = nx.Graph()
G.add_nodes_from(categories_count_df["category"])
plt.figure(1, figsize=(15, 15))
nx.draw_networkx(G, node_size=nodes_size_list_normalized, with_labels=True)
plt.show()

# Adding edges for each point couple where d<50m
# Solution 1 : bruteforce
sorted_points_by_cat = points_by_category.sort_values("category")
entities_by_cat_count = (points_by_category.value_counts("category").reset_index()
                         .rename(columns={"index": "category", 0: "count"}).sort_values("category"))

# index début cat = index fin (cat prec) + 1
# index fin =  index début cat + val cat -1
# => index début = sum(val de toutes les cat précédentes)

"""min_dist = 50
current_cat = ""
current_cat_count = 0
total_cat_count = 0
for i, row_a in sorted_points_by_cat.iterrows():
    a_lat = row_a["latitude"]
    a_long = row_a["longitude"]
    if current_cat != row_a["category"]:
        current_cat = row_a["category"]
        current_cat_count = entities_by_cat_count.loc[entities_by_cat_count["category"] == current_cat, "count"].iloc[0]
        total_cat_count = total_cat_count + current_cat_count
    for j, row_b in sorted_points_by_cat.iloc[total_cat_count: len(sorted_points_by_cat.index)-1].iterrows():
        b_lat = row_b["latitude"]
        b_long = row_b["longitude"]
        dist_a_b = distance.distance((a_lat, a_long), (b_lat, b_long)) #distance from Geopy
        if dist_a_b < min_dist:
            G.add_edge(row_a["category"], row_b["category"])"""

# Solution 2 : manual matrix
"""matrix_shape = [sorted_points_by_cat.index, sorted_points_by_cat.index]
matrix = np.array(shape=matrix_shape, dtype=np.bool_)
i = 0
j = 0
while i < 1:
    if i > j:
        continue
    while j < len(sorted_points_by_cat.index)-1:
        if sorted_points_by_cat["category"].iloc[i] != sorted_points_by_cat["category"].iloc[j]:
            lat_a_b = (sorted_points_by_cat["latitude"].iloc[i], sorted_points_by_cat["longitude"].iloc[i])
            long_a_b = (sorted_points_by_cat["latitude"].iloc[j], sorted_points_by_cat["longitude"].iloc[j])
            if distance.distance(lat_a_b, long_a_b):
                matrix[i, j] = 1
            else:
                matrice[i, j] = 0
        j += 1
    i += 1"""

# Solution 3 : using scipy matrix
"""matrix = distance.cdist(coordinate_list, coordinate_list, lambda a,b: geopy.distance.distance(a,b).meters)
i = 0
j = 0
for i in matrix:
    for j in matrix:
        if matrix[i][j] < 50:
            G.add_edge(points_by_category["category"].iloc[i], points_by_category["category"].iloc[j])
plt.show()"""

# Solution 4 : accelerating structure
"""loop through matrix M de n x m dimensions vides, avec n (max) < lat max et m (max) < long max : 
    loop dans df pour stocker l'index de chaque point dans les ranges correspondantes

L = liste
loop sur chaque case de M :
    loop sur tous les points P de la case : 
        loop sur la case et les cases adjacentes
            si d < 50 :
                add les deux indexes dans un tuple 
                add le tuple dans L

loop sur L : 
     si index 1 et 2 sont de catégories différentes : 
        créer une edge"""

# Display graph
with open("testdump.json", 'r', encoding='utf-8') as test:
    graph_data = json.load(test)

H = nx.node_link_graph(graph_data, directed=False, multigraph=True)

pos = nx.circular_layout(H)
#nx.draw_networkx(H, pos=pos, node_size=nodes_size_list_normalized)
#plt.show()


# Create multi-edges with width depending on the number of relation between two nodes
edges = []
u_list = []

for u in H:
    u_list.append(u)
    for v in H:
        if v not in u_list:
            if H.number_of_edges(u, v) != 0:
                edges.append((u, v, H.number_of_edges(u, v)))

H.clear_edges()
H.add_weighted_edges_from(edges)

widths = nx.get_edge_attributes(H, 'weight')
width_list = list(widths.values())
normalized_width_list = [x/max(width_list)*40 for x in width_list]

pos = nx.circular_layout(H)
nx.draw_networkx_nodes(H, pos=pos, node_size=nodes_size_list_normalized)
nx.draw_networkx_edges(H, pos, edgelist=widths.keys(), width=normalized_width_list, alpha=0.8)
nx.draw_networkx_labels(H, pos)
plt.show()