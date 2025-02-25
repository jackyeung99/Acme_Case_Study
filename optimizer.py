import numpy as np
from scipy.optimize import linprog
from helpers import *

def optimize_linear_contributions(children, c_func, constraint_func=None, constraint_value=None, budget=1):
    """
    Solves the linear optimization problem with an interchangeable objective function.
    
    Parameters:
    - children: List of objects, each with attributes like `target1`, `target2`, etc.
    - c_func: Function to define the objective coefficients for optimization (e.g., lambda x: x.target1)
    - constraint_func: Function to define an additional constraint (e.g., lambda x: x.target2)
    - constraint_value: The constraint threshold (e.g., ensure total target2 score is at least X)
    - budget: Total budget to distribute across units (default = 1)

    Returns:
    - List of optimized contributions for each unit
    """
    num_units = len(children)

    # Weighted array for 
    c = -np.array([c_func(x) for x in children])  
    # print(c)

    A_eq = [np.ones(num_units)]
    b_eq = [budget]


    A_ub, b_ub = None, None
    if constraint_func and constraint_value is not None:
        A_ub = [[-constraint_func(x) for x in children]]  # Ensure target2 stays above the threshold
        b_ub = [-constraint_value]

    bounds = [(x.Min_Contribution, x.Max_Contribution) for x in children]
    result = linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if result.success:
        return result.x
    else:
        raise ValueError("Linear optimization failed!")

def bottom_up_optimizer(node, target_func, constraint_func=None, constraint_value=None):
    """
    Recursively optimizes contribution percentages in a bottom-up manner.
    """
    if not node.sub_units:  
        return

    # Recursively optimize children first
    for child in node.sub_units:
        bottom_up_optimizer(child, target_func, constraint_func, constraint_value)

    # After children are optimized, optimize this level
    children = node.sub_units
    results = optimize_linear_contributions(children, target_func, constraint_func, constraint_value)
    
    # update contributions
    for child, new_contribution in zip(children, results):
        # print(child.Contribution, new_contribution)
        child.Contribution = new_contribution

    #propagate values up
    update_vals(node)

    return node

    
### Cost function 
def update_vals(node):
    ''' 
    Function to aggregate one layer values for each sub-company to their respective parent 

    '''
    
    children = getattr(node, 'sub_units', [])
    
    total_revenue = 0
    total_weighted_margin = 0
    volatilities = []

    # Taking a weighted average for the level based on contribution ammounts
    for child in children:
        total_revenue += child.Revenue * child.Contribution
        total_weighted_margin += child.Revenue * child.Contribution * child.Margin

        if child.Volatility is not None and child.Volatility != 0:
            volatilities.append(child.Volatility * child.Contribution)

    avg_volatility = np.mean(volatilities) if volatilities else 0

    node.Revenue = total_revenue
    node.Volatility = avg_volatility
    node.Weighted_Margin = total_weighted_margin




def eval_optimizer(optimized_contributions):
    print("---------------- Contributions by each sub company ----------------")
    print_tree(optimized_contributions)
    results = {
            'Revenue': optimized_contributions.Revenue,
            'Volatility': optimized_contributions.Volatility,
            'Weighted_Margin': optimized_contributions.Weighted_Margin
        }


    return results
