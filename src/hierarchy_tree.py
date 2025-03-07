import numpy as np
import pandas as pd
import networkx as nx
import plotly.express as px
from collections import deque
from itertools import count
import copy

from src.unit_class import Unit
from data.hierarchy import Acme
from src.optimizer import ContributionOptimizer
from figure_settings.fig_settings import *

class HierarchyTree:
    def __init__(self, parameters = None):
        self.build_tree(parameters)

    def build_tree(self, parameters):
        """Builds and processes a new tree copy."""
        self.root = self.build_tree_recursively(Acme)
        
        if parameters:
            self.root.update_parameters(parameters)
        
        self.propagate_trends_down()
        self.normalize_contributions()
        self.update_all()

    def build_tree_recursively(self, hierarchy_dict):
        """Recursively builds the hierarchical tree."""

            
        # copying Unit isntance in acme hierarchy
        current_unit = Unit(
            name=hierarchy_dict['Unit'].name,
            revenue=hierarchy_dict['Unit'].revenue,
            margin=hierarchy_dict['Unit'].margin,
            min_trend=hierarchy_dict['Unit'].min_trend,
            max_trend=hierarchy_dict['Unit'].max_trend,
            max_contribution=hierarchy_dict['Unit'].max_contribution,
            min_contribution=hierarchy_dict['Unit'].min_contribution,
        )

        current_unit.clear_sub_units()

        for child_dict in hierarchy_dict.get('Children', []):
            child_unit = self.build_tree_recursively(child_dict)
            current_unit.add_sub_unit(child_unit)

        return current_unit


    def optimize(self, weights):
        """Optimizes the tree using a ContributionOptimizer instance."""
        optimizer = ContributionOptimizer()
        self.root = optimizer.optimize(self.root, weights)
    
    def evaluate(self, root=None):
        """ Recalculate dependent variables based on contributions """
        if root is None:
            root = self.root
        return {
            'Revenue': root.revenue,
            # 'Volatility': root.volatility,
            'Avg Margin': root.margin,
            'Profit': root.margin_dollars
        }
    

    def propagate_trends_down(self, root=None):
        """Recursively propagate trends to all child nodes."""
        if root is None:
            root = self.root

        for child in root.sub_units: 
            child.min_trend = (1 + child.min_trend) * (1 + root.min_trend) - 1
            child.max_trend = (1 + child.max_trend) * (1 + root.max_trend) - 1
            self.propagate_trends_down(child)

    def normalize_contributions(self, budget=1):
        """Normalizes contributions at each level."""

        queue = deque([self.root]) 

        while queue:
            node = queue.popleft()
            children = getattr(node, 'sub_units', [])

            if not children:
                continue  #

            min_total = sum(child.min_contribution for child in children)
            max_total = sum(child.max_contribution for child in children)

            # scale contributions if the current is impossible
            if min_total > budget or max_total < budget:
                max_scaler = 1.5 / max_total if max_total > 0 else 1
                min_scaler = .5 / min_total if min_total > 0 else 1
                for child in children:
                    child.max_contribution = min((child.max_contribution * max_scaler), 1)
                    child.min_contribution *= min_scaler 
                    child.contribution = (child.max_contribution + child.min_contribution) /2
            
            node._update_values()
            queue.extend(children)

    def update_all(self, root=None):
        """Recursively update revenue, margin, and volatility."""
        
        if root is None:
            root = self.root

        if not root.sub_units:
            return

        for child in root.sub_units:
            self.update_all(child) 

        total_revenue, total_margin, volatilities = 0, 0, 0
        for child in root.sub_units:
            total_revenue += child.contribution * child.revenue
            total_margin += child.contribution * child.margin

            if child.volatility is not None and child.volatility != 0:
                volatilities += child.contribution * child.volatility

        root.revenue = total_revenue
        root.margin = total_margin
        root.volatility = volatilities
        root.margin_dollars = root.revenue * root.margin

    def random_walk(self, node, years=5):
        """
        Performs a single simulation for a given sub-unit over a time horizon
        using a geometric brownian motion.
        """

        mu = (node.min_trend + node.max_trend) / 2
        sigma = (np.abs(node.max_trend - node.min_trend)) / 4  # 95% confidence range
        shock_probability = np.abs(node.max_trend - node.min_trend) * .001

        # Generate a single trajectory of growth rates
        # growth_rates = np.random.normal(loc=mu, scale=sigma, size=years)
        growth_rates = np.random.lognormal(mean=mu, sigma=sigma, size=years)
        growth_rates = np.clip(growth_rates, node.min_trend, node.max_trend)

        revenue_trajectory = np.zeros(years+1)
        revenue_trajectory[0] = node.revenue  

        # Simulate revenue using random walk
        dt = 1/12
        for t in range(1, years+1):
            epsilon = np.random.randn() 
            revenue_trajectory[t] = revenue_trajectory[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * epsilon)


        # black swan event 
        if np.random.rand() < shock_probability:
            shock_magnitude = np.random.uniform(-0.3, 0.5)  # Loss up to 30% or gain up to 50%
            revenue_trajectory[t] *= (1 + shock_magnitude)


        node.revenue = revenue_trajectory[-1]



    def simulation(self, years=5, target_layer=5):
        """
        Performs random walk on all segments and updates depedencies based on new revenues

        """
        root =  self.copy_hierarchy()
        queue = deque([(root, 0)])  

        while queue:
            node, level = queue.popleft()

            if level == target_layer:
                self.random_walk(node, years)
    
            
            elif level < target_layer:
                # Continue traversal if below layer 5
                for child in node.sub_units:
                    queue.append((child, level + 1))
        
        self.update_all(root)
        return self.evaluate(root)
    

    
    def build_graph(self, graph, node, parent_name=None, unique_id_counter=None):
        """Recursively builds a network graph for visualization."""
        if unique_id_counter is None:
            unique_id_counter = count()  

        node_name = node.name  
        unique_node_id = f"{next(unique_id_counter)}"

        revenue = getattr(node, 'revenue', 0)
        margin = getattr(node, 'margin', 0)
        min_trend = getattr(node, 'min_trend', 0)
        max_trend = getattr(node, 'max_trend', 0)
        contribution = getattr(node, 'contribution')

        label = (
            f"{node_name}\n"
            f"Rev: {round(revenue, 3)}\n"
            f"Margin: {round(margin, 3)}\n"
            f"Trend: [{round(min_trend, 3)}, {round(max_trend, 3)}]\n"
            f"Contrib:  {round(contribution, 3)}"
        )

        graph.add_node(unique_node_id, label=label, revenue=revenue)

        if parent_name:
            graph.add_edge(parent_name, unique_node_id)

        for child in node.sub_units:
            self.build_graph(graph, child, unique_node_id, unique_id_counter)

    def print_tree(self):
        """Generates and displays a hierarchical visualization of the tree."""
        unique_id_counter = count()  
        G = nx.DiGraph() 


        self.build_graph(G, self.root, unique_id_counter=unique_id_counter) 

        plt.figure(figsize=(30, 15))

        pos = nx.nx_agraph.graphviz_layout(G, prog="dot", args="-Gnodesep=4")
        labels = nx.get_node_attributes(G, 'label')

        nx.draw(G, pos, with_labels=True, labels=labels, 
                node_size=10000, cmap=plt.cm.Blues, 
                edge_color="gray", font_size=12)

        plt.title("Company Hierarchy Visualization with Financial Details", fontsize=35)
        plt.show()

    def to_dataframe(self):
        """Recursively build a DataFrame representation of the hierarchy."""
        rows = []

        queue =deque([(self.root, 0)])
        while queue:
            node, level = queue.popleft()
            rows.append({
                'Level': level,
                'Name': node.name,
                'Total Revenue': node.revenue,
                'Margin': node.margin,
                'Contribution': node.contribution,
                'Min_Contribution': node.min_contribution,
                'Max_Contribution': node.max_contribution,
                'Min_Trend': node.min_trend,
                'Max_Trend': node.max_trend,
            })

            for child in node.sub_units:
                queue.append((child, level+1))



        return pd.DataFrame(rows)
    

    def print_df(self):
        df = self.to_dataframe()
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df.to_string(index=False))


    def copy_hierarchy(self, root=None):
        """Creates a deep copy of the unit and its sub-units without recalculating values."""

        if root is None:
            root = self.root

        new_unit = Unit.__new__(Unit)
    
        # Manually copy over attributes
        new_unit.name = root.name
        new_unit.revenue = root.revenue
        new_unit.margin = root.margin
        new_unit.min_trend = root.min_trend
        new_unit.max_trend = root.max_trend
        new_unit.max_contribution = root.max_contribution
        new_unit.min_contribution = root.min_contribution
        new_unit.contribution = root.contribution  
        new_unit.margin_dollars = root.margin_dollars
        new_unit.volatility = root.volatility
        
        # Deep copy of sub-units
        new_unit.sub_units = [self.copy_hierarchy(child) for child in root.sub_units]
        
        return new_unit