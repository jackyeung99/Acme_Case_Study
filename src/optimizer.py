import numpy as np
from scipy.optimize import  minimize
from src.helpers import *



def objective(contributions, children, weights):
    """
    Objective function to optimize based on revenue, margin, growth, and volatility.
    """
    alpha = weights.get("alpha", 0.5)  # Default values if not provided
    beta = weights.get("beta", 0.5)
    gamma = weights.get("gamma", 0.2)
    delta = weights.get("delta", 0.1)

    revenues = np.array([child.revenue for child in children], dtype=np.float64)
    margins = np.array([child.margin for child in children])
    growth = np.array([child.max_trend - child.min_trend for child in children])  
    volatilities = np.array([np.abs(child.max_trend - child.min_trend) for child in children])

    # Standardization
    for arr in [revenues, margins, growth, volatilities]:
        if np.std(arr) > 0:
            arr -= np.mean(arr)
            arr /= np.std(arr)

    # Weighted Sum
    weighted_objective = np.sum(
        contributions * (alpha * revenues + beta * margins + gamma * growth - delta * volatilities)
    )

    return -weighted_objective 


def optimize_contributions(children, weights):
    """
    Optimizes contribution percentages based on weighted objective and contribution constraints.
    """
    x0 = [x.contribution for x in children]
    bounds = [(child.min_contribution, child.max_contribution) for child in children]
    constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    # Optimize
    result = minimize(
        objective, x0, args=(children, weights),
        constraints=[constraint], bounds=bounds, method='SLSQP'
    )

    if result.success:
        return result.x  # Optimal contributions
    else:
        return x0  # Default to initialized values


def bottom_up_optimizer(node, weights):
    """
    Recursively optimizes contribution percentages in a bottom-up manner.
    """
    if not node.sub_units:  
        return node

    # Recursively optimize children first
    for child in node.sub_units:
        bottom_up_optimizer(child, weights)

    children = node.sub_units

    if len(children) == 1:
        results = [1]
    else:
        results = optimize_contributions(children, weights)
    
    # Update contributions
    for child, new_contribution in zip(children, results):
        child.contribution = new_contribution

    node._update_values()
    return node



def eval_optimizer(optimized_contributions):
    return {
            'Revenue': optimized_contributions.revenue,
            'Volatility': optimized_contributions.volatility,
            'Avg Margin': optimized_contributions.margin,
            'Profit': optimized_contributions.margin_dollars
        }
