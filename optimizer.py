import numpy as np
from bayes_opt import BayesianOptimization
from scipy.optimize import linprog, minimize
from helpers import *


def objective(contributions, children, alpha):
    beta = 1 - alpha
    """ Objective function to maximize revenue and margin percentage. """
    revenues = np.array([child.revenue for child in children])
    margins = np.array([child.margin for child in children])

    if np.std(revenues) > 0:
        revenues = (revenues - np.mean(revenues)) / np.std(revenues)
    if np.std(margins) > 0:
        margins = (margins - np.mean(margins)) / np.std(margins)

    weighted_objective = np.sum(contributions * (alpha * revenues + beta * margins))
    
    return -weighted_objective  

def optimize_contributions(children, alpha=0.5):


    x0 = [x.contribution for x in children]
    bounds = [(child.min_contribution, child.max_contribution) for child in children]
    constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

    # Optimize
    result = minimize(
        objective, x0, args=(children, alpha),
        constraints=[constraint], bounds=bounds, method='SLSQP'
    )

    if result.success:
        return result.x  # Optimal contributions
    else:
        return x0




def bottom_up_optimizer(node, alpha):
    """
    Recursively optimizes contribution percentages in a bottom-up manner.
    """
    if not node.sub_units:  
        return node

    # Recursively optimize children first
    for child in node.sub_units:
        bottom_up_optimizer(child, alpha)

 
    children = node.sub_units

    if len(children) == 1:
        results = [1]
    else:
        results = optimize_contributions(children, alpha)
    
    # update contributions
    for child, new_contribution in zip(children, results):
        # print(child.Contribution, new_contribution)
        child.contribution = new_contribution


    node._update_values()
    return node


def eval_optimizer(optimized_contributions):
    return {
            'Revenue': optimized_contributions.revenue,
            'Volatility': optimized_contributions.volatility,
            'Avg Margin': optimized_contributions.margin,
            'Margin Dollars': optimized_contributions.margin_dollars
        }
