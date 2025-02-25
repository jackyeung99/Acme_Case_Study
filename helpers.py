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
    current_unit.clear_units()
    # Iterate over each child dictionary in the 'Children' list
    for child_dict in hierarchy_dict.get('Children', []):
      
        child_unit = build_tree_recursion(child_dict)
        # Attach the child unit to the current unit
        current_unit.add_unit(child_unit)

    return current_unit


def build_tree(hierarchy_dict):
    root = build_tree_recursion(hierarchy_dict)
    # transformations to make this usable
    propagate_trends_down(root)
    normalize_contributions(root)
    update_vals_recursive(root)
    return root


def update_vals_recursive(node):
    ''' 
    Recursively aggregates values for each sub-company to their respective parent.
    Weighted Margin is manually calculated using the newly updated total revenue.
    '''
    
    children = getattr(node, 'sub_units', [])

    if not children:
        # Base case: If there are no children, return the node's own values
        return node.Revenue, node.Volatility, node.Weighted_Margin

    total_revenue = 0
    volatilities = []
    
    # First, recursively update children and compute total revenue
    for child in children:
        child_revenue, child_volatility, _ = update_vals_recursive(child)  # Ignore child_weighted_margin
        total_revenue += child_revenue * child.Contribution

        if child_volatility is not None and child_volatility != 0:
            volatilities.append(child_volatility * child.Contribution)

    avg_volatility = np.mean(volatilities) if volatilities else 0

    # Now compute total weighted margin using updated total revenue
    total_weighted_margin = sum(
        (child.Margin * total_revenue * child.Contribution) for child in children
    )

    # Update parent node with aggregated values
    node.Revenue = total_revenue
    node.Volatility = avg_volatility
    node.Weighted_Margin = total_weighted_margin

    return node.Revenue, node.Volatility, node.Weighted_Margin



def propagate_trends_down(node):
    """
    Recursively propagate trends to descendents
    
    """
    min_trend = getattr(node, 'Min_Trend', 0)
    max_trend = getattr(node, 'Max_Trend', 0)

    for child in getattr(node, 'sub_units', []):
        child.Min_Trend = (1 + getattr(child, 'Min_Trend', 0)) * (1 + min_trend) - 1
        child.Max_Trend = (1 + getattr(child, 'Max_Trend', 0)) * (1 + max_trend) - 1
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
        min_total = sum(child.Min_Contribution for child in children)
        max_total = sum(child.Max_Contribution for child in children)

        # scale contributions if the current is impossible
        if min_total > budget or max_total < budget:
            max_scaler = 1.5 / max_total if max_total > 0 else 1
            min_scaler = .5 / min_total if min_total > 0 else 1
            for child in children:
                child.Max_Contribution = min((child.Max_Contribution * max_scaler), 1)
                child.Min_Contribution *= min_scaler 


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
            'Name': getattr(node, 'Name', None),
            'Revenue': getattr(node, 'Revenue', None),
            'Weighted_Revenue': getattr(node, 'Weighted_Revenue', 0),
            'Margin': getattr(node, 'Margin', 0),
            'Weighted_Margin': getattr(node, 'Weighted_Margin', None),
            'Contribution': getattr(node, 'Contribution', 0),
            'Min_Contribution': getattr(node, 'Min_Contribution', None),
            'Max_Contribution': getattr(node, 'Max_Contribution', None),
            'Min_Trend': getattr(node, 'Min_Trend', None),
            'Max_Trend': getattr(node, 'Max_Trend', None),
        }

        if row['Min_Trend'] and row['Max_Trend']:
            row['Volatility'] = row['Max_Trend'] - row['Min_Trend']
        else:
            row['Volatility'] = None


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
    
