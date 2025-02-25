from collections import deque
import numpy as np
import matplotlib.pyplot as plt
from helpers import *
from optimizer import *

def monte_carlo_simulation(node, years=5):
    """
    Performs a single Monte Carlo simulation for a given sub-unit over a time horizon
    using a Gaussian distribution for revenue growth.

    Parameters:
    - node: The node representing the business unit.
    - years: Number of years to simulate.

    Returns:
    - results: Dictionary containing revenue statistics.
    """
    # Compute mean (µ) and standard deviation (σ) for the growth rate
    mean_growth = (node.Min_Trend + node.Max_Trend) / 2
    std_dev_growth = (node.Max_Trend - node.Min_Trend) / 4  # 95% confidence range

    # Generate a single trajectory of growth rates
    growth_rates = np.random.normal(loc=mean_growth, scale=std_dev_growth, size=years)
    growth_rates = np.clip(growth_rates, node.Min_Trend, node.Max_Trend)

 
    revenue_trajectory = np.zeros(years)
    revenue_trajectory[0] = node.Revenue  # Start with current revenue

    # Simulate revenue using random walk
    for t in range(1, years):
        revenue_trajectory[t] = revenue_trajectory[t-1] * (1 + growth_rates[t])

    # Update node revenue based on the final year of simulation
    node.Revenue = revenue_trajectory[-1]
    node.Weighted_Margin = revenue_trajectory * node.Margin  


def run_monte_carlo_layer_5(root, years=5, target_layer=5):
    """
    Randomizes the revenue based on the trends for all of the sub categories
    
    Parameters:
    - root: The root node of the tree.
    - years: Number of years to simulate.
    - num_simulations: Number of Monte Carlo iterations.
    - target_layer: The specific layer to run simulations on (default = 5).
    
    Returns:
    - Dictionary mapping layer-5 sub-units to their simulation results.
    """
    # Dictionary to store results
    simulation_results = {}

    # Perform level-order traversal to track depth of nodes
    queue = deque([(root, 1)])  # Start from level 1

    while queue:
        node, level = queue.popleft()

        # If node is at the target layer, run Monte Carlo to simulate random walk modifying node in place
        if level == target_layer:
            monte_carlo_simulation(node, years)
         
        elif level < target_layer:
            # Continue traversal if below layer 5
            for child in node.sub_units:
                queue.append((child, level + 1))

    return simulation_results


def run_strategy(root, years, n=20):
    """
    Runs Monte Carlo simulations for a given strategy.

    Parameters:
    - root: The root node of the strategy.
    - years: Number of years to simulate.
    - n: Number of Monte Carlo iterations.

    Returns:
    - A dictionary containing the results.
    """
    weighted_margin = []
    revenue = []

    for i in range(n):  # Fix loop syntax
        temp_root = root.copy()
        run_monte_carlo_layer_5(temp_root, years)
        update_vals_recursive(temp_root)
        results = eval_monte(temp_root)

        weighted_margin.append(results['Weighted_Margin'])
        revenue.append(results['Revenue'])

    return {
        "revenue": revenue,
        "weighted_margin": weighted_margin
    }


def run_all_strategies(strategies, years):
    """
    Runs multiple strategies and stores results over different years.

    Parameters:
    - strategies: List of strategies (root nodes).
    - years: List of years to simulate.

    Returns:
    - A list of dictionaries containing results for each year.
    """
    all_results = []

    for strat_name, strat_root in strategies:
        
        strategy = {'Name': strat_name,}
        revenue = []
        margin = []
        for year in range(1, years+1):
            result = run_strategy(strat_root, year)

            revenue.append(result['revenue'])
            margin.append(result['weighted_margin'])

        strategy['revenue'] = revenue
        strategy['margin'] = margin
        all_results.append(strategy)

    return all_results

def eval_monte(optimized_contributions):
    results = {
            'Revenue': optimized_contributions.Revenue,
            'Volatility': optimized_contributions.Volatility,
            'Weighted_Margin': optimized_contributions.Weighted_Margin
        }


    return results