import plotly.express as px
import pandas as pd
import networkx as nx
from figure_settings.fig_settings import *
from itertools import count

unique_id_counter = count()

def build_graph(graph, node, parent_name=None):
    node_name = node.name  
    unique_node_id = f"{next(unique_id_counter)}"
    revenue = getattr(node, 'revenue', "N/A")
    margin = getattr(node, 'margin', "N/A")
    min_trend = getattr(node, 'min_trend', "N/A")
    max_trend = getattr(node, 'max_trend', "N/A")
    min_contribution = getattr(node, 'min_contribution', "N/A")
    max_contribution = getattr(node, 'max_contribution', "N/A")

    label = (
        f"{node_name}\n"
        f"Rev: {round(revenue,3)}\n"
        f"Margin: {margin}\n"
        f"Trend: [{round(min_trend, 3)}, {round(max_trend,3)}]\n"
        f"Contrib: [{round(min_contribution,3)}, {round(max_contribution,3)}]"
    )

    # Add node to the graph
    graph.add_node(unique_node_id, label=label, revenue=revenue)

    # Connect to parent if applicable
    if parent_name:
        graph.add_edge(parent_name, unique_node_id)

    # Recursively add child nodes
    for child in node.sub_units:
        build_graph(graph, child, unique_node_id)

def visualize_tree(root):
    """
    Generates a hierarchical visualization of the company structure, 
    including revenue, margin, contribution limits, and trends.

    Parameters:
    - tree: List of dictionaries representing the hierarchical company structure.
    """
    G = nx.DiGraph() 
    build_graph(G, root)

    plt.figure(figsize=(30, 15))
    
    pos = nx.nx_agraph.graphviz_layout(G, prog="dot", args="-Gnodesep=4")
    labels = nx.get_node_attributes(G, 'label')
    
    # Draw the network
    nx.draw(G, pos, labels=labels, with_labels=True, node_size=10000,  cmap=plt.cm.Blues, edge_color="gray", font_size=12)


    plt.title("Company Hierarchy Visualization with Financial Details", fontsize=25)
    plt.show()