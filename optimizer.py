import numpy as np
from bayes_opt import BayesianOptimization
from scipy.optimize import linprog
from helpers import *

# def optimize_linear_contributions(children, c_func, constraint_func=None, constraint_value=None, budget=1):
#     """
#     Solves the linear optimizer for each layer
#     """
#     num_units = len(children)

#     # Weighted array for 
#     c = -np.array([c_func(x) for x in children])  
#     # print(c)

#     A_eq = [np.ones(num_units)]
#     b_eq = [budget]


#     A_ub, b_ub = None, None
#     if constraint_func and constraint_value is not None:
#         A_ub = [[-constraint_func(x) for x in children]]  # Ensure target2 stays above the threshold
#         b_ub = [-constraint_value]

#     bounds = [(x.min_contribution, x.max_contribution) for x in children]
#     result = linprog(c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

#     if result.success:
#         return result.x
#     else:
#         print("⚠️ Linear optimization failed! Attempting fallback...")
#         print("Failure Reason:", result.message)
#         return [x.min_contribution for x in children]
    

# bayesian 
def target_function(children, alpha=0.5, beta=0.5, **kwargs):
    """
    Objective function for Bayesian optimization.

    Parameters:
    - children: List of child units (each with revenue, margin, etc.)
    - alpha: Weight for revenue maximization
    - beta: Weight for margin maximization
    - kwargs: Contributions suggested by optimizer

    Returns:
    - Objective value with penalties for constraint violations
    """

    # Extract contributions from optimizer's suggested values
    contributions = np.array([kwargs[f'c{i}'] for i in range(len(children))])


    sum_constraint_penalty = 0
    if not np.isclose(sum(contributions), 1.0):
        sum_constraint_penalty = -100000 * abs(sum(contributions) - 1)

    objective_value = sum(
        contrib * child.revenue
        for contrib, child in zip(contributions, children)
    )

    if np.any(contributions < 0) or np.any(contributions > 1): 
        return -np.inf

    return -(objective_value + sum_constraint_penalty) 

def bayesian_optimize_contributions(children, n_iter=50, alpha=0.5, beta=0.5):
    """
    Uses Bayesian Optimization to find the best contribution allocations.

    Parameters:
    - children: List of units with attributes like `revenue`, `margin`, `contribution`
    - n_iter: Number of iterations for Bayesian optimization
    - alpha: Weight for revenue
    - beta: Weight for margin

    Returns:
    - Optimal contributions for each unit
    """
    
    num_units = len(children)

    # Define parameter bounds for each unit's contribution
    pbounds = {f'c{i}': (child.min_contribution, child.max_contribution) for i, child in enumerate(children)}

    # Initialize Bayesian Optimizer
    optimizer = BayesianOptimization(
        f=lambda **kwargs: target_function(children, alpha, beta, **kwargs),  # Fix: Defer function execution
        pbounds=pbounds,  
        random_state=42,
        verbose=0
    )

    # Run Bayesian optimization
    optimizer.maximize(init_points=5, n_iter=n_iter)

    # Extract optimal contributions
    best_contributions = optimizer.max["params"]
    return [best_contributions[f'c{i}'] for i in range(num_units)]






def bottom_up_optimizer(node, alpha, beta):
    """
    Recursively optimizes contribution percentages in a bottom-up manner.
    """
    if not node.sub_units:  
        return

    # Recursively optimize children first
    for child in node.sub_units:
        bottom_up_optimizer(child, alpha, beta)

    # After children are optimized, optimize this level
    children = node.sub_units

    # results = optimize_linear_contributions(children, target_func, constraint_func, constraint_value)
    results = bayesian_optimize_contributions(children, alpha, beta)
    
    # update contributions
    for child, new_contribution in zip(children, results):
        # print(child.Contribution, new_contribution)
        child.contribution = new_contribution

    #propagate values up
    node._update_values()

    return node


def eval_optimizer(optimized_contributions):
    print("---------------- Contributions by each sub company ----------------")
    print_tree(optimized_contributions)
    results = {
            'Revenue': optimized_contributions.revenue,
            'Volatility': optimized_contributions.volatility,
            'Avg Margin': optimized_contributions.margin,
            'Margin Dollars': optimized_contributions.margin_dollars
        }


    return results
