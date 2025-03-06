from collections import deque
import numpy as np
from src.hierarchy_tree import HierarchyTree
from src.optimizer import *


# intervals per year
INTERVAL = 12

def run_simulations(weights, years, parameters=None, n=20):
    """
    Runs n simulations
    """
    margin = []
    revenue = []
    temp_root = HierarchyTree(parameters)
    temp_root.optimize(weights)
    for i in range(n): 
        # randomizes revenue based on trend data
        results = temp_root.simulation(years)

        margin.append(results['Profit'])
        revenue.append(results['Revenue'])

    return {
        "revenue": revenue,
        "margin": margin
    }


def run_all_simulations(strategies, years, parameters):
    """
    Runs multiple strategies and stores results over different years.

    Parameters:
    - strategies: List of strategies (root nodes).
    - years: List of years to simulate.

    Returns:
    - A list of dictionaries containing results for each year.
    """
    all_results = []

    for strat_name, weights in strategies:
        strategy = {'Name': strat_name}
        revenue = []
        margin = []
        for step in range(1, years*INTERVAL+1):
            result = run_simulations(weights, step, parameters)
            revenue.append(result['revenue'])
            margin.append(result['margin'])

        strategy['revenue'] = revenue
        strategy['margin'] = margin
        all_results.append(strategy)


    return all_results

