import numpy as np
import pandas as pd
from collections import deque

def build_tree_recursion(hierarchy_dict):
    """
    Recursively build a hierarchical tree from a dictionary.

    Each node in the dictionary should have:
      - 'Unit': an object representing the node (with attributes like Revenue, Margin, Trend, Contribution, etc.)
      - 'Children': a list of child node dictionaries (each with the same structure).

    The function adds each child unit to its parent's children list using the parent's `add_unit` method.

    Parameters:
      hierarchy_dict (dict): A dictionary representing a tree node.

    Returns:
      The root Unit object with its children attached.
    """
    # Get the current node's Unit object
    current_unit = hierarchy_dict.get('Unit')
    current_unit.clear_sub_units()
    # Iterate over each child dictionary in the 'Children' list
    for child_dict in hierarchy_dict.get('Children', []):
        child_unit = build_tree_recursion(child_dict)
        # Attach the child unit to the current unit
        current_unit.add_sub_unit(child_unit)

    return current_unit


def build_tree(hierarchy_dict):
    root = build_tree_recursion(hierarchy_dict)
    # transformations to make this usable
    propagate_trends_down(root)
    normalize_contributions(root)
    return root

def propagate_trends_down(node):
    """
    Recursively propagate trends to descendents
    
    """
    min_trend = getattr(node, 'min_trend', 0)
    max_trend = getattr(node, 'max_trend', 0)

    for child in getattr(node, 'sub_units', []):
        child.min_trend = (1 + getattr(child, 'min_trend', 0)) * (1 + min_trend) - 1
        child.max_trend = (1 + getattr(child, 'max_trend', 0)) * (1 + max_trend) - 1
        # Recursively propagate to the next level
        propagate_trends_down(child)



def normalize_contributions(root, budget=1):
    """
    Normalizes Min_Contribution and Max_Contribution in a hierarchical tree structure,
    ensuring that each level is normalized before moving to deeper levels.

    - If both min and max contributions are zero, distributes the budget equally.
    - If total min contributions exceed the budget, they are proportionally scaled down.
    - If total max contributions are below the budget, they are proportionally scaled up.
    - Ensures Min_Contribution does not exceed Max_Contribution.

    Parameters:
    - root: Root node of the hierarchical tree (Node object with sub_units).
    - budget: Total budget to distribute among children at each level.
    """

    queue = deque([root])  # Process level by level using a queue

    while queue:
        node = queue.popleft()
        children = getattr(node, 'sub_units', [])

        if not children:
            continue  # No children, nothing to normalize

        # Compute total min and max contributions at the current level
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
        # Add children to queue for next level processing
        queue.extend(children)



def build_df(root):
    """
    Recursively traverses the tree starting at `root` and prints a DataFrame
    where each row represents a node with its level in the hierarchy.
    
    Each Unit is assumed to have attributes:
      - name
      - Revenue, Margin, Trend, Contribution (if not present, default to 0)
      - Min_Contribution, Max_Contribution, Min_Trend, Max_Trend (if available)
      - children: a list of child Unit objects
      
    Parameters:
      root (Unit): The root node of the tree.
    """
    rows = []
    
    def traverse(node, level):
        # Create a row for the current node, using getattr with defaults.
        row = {
            'Level': level,
            'Name': getattr(node, 'name', None),
            'Total Revenue': getattr(node, 'revenue', None),
            'Margin': getattr(node, 'margin', 0),
            'Contribution': getattr(node, 'contribution', 0),
            'Min_Contribution': getattr(node, 'min_contribution', None),
            'Max_Contribution': getattr(node, 'max_contribution', None),
            'Min_Trend': getattr(node, 'min_trend', None),
            'Max_Trend': getattr(node, 'max_trend', None),
        }


        rows.append(row)
        # Recursively traverse children if they exist
        for child in getattr(node, 'sub_units', []):
            traverse(child, level + 1)
    
    traverse(root, 0)
    df = pd.DataFrame(rows)
    return df


def print_tree(root):
    df = build_df(root)
    sorted_df = df.sort_values(by='Level')

    with pd.option_context('display.max_rows', None):
      print(sorted_df.to_string(index=False))
    
