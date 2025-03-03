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
    mean_growth = (node.min_trend + node.max_trend) / 2
    std_dev_growth = (node.max_trend - node.min_trend) / 4  # 95% confidence range

    # Generate a single trajectory of growth rates
    growth_rates = np.random.normal(loc=mean_growth, scale=std_dev_growth, size=years)

    growth_rates = np.clip(growth_rates, node.min_trend, node.max_trend)

    revenue_trajectory = np.zeros(years+1)
    revenue_trajectory[0] = node.revenue  

    # Simulate revenue using random walk
    for t in range(1, years+1):
        revenue_trajectory[t] = revenue_trajectory[t-1] * (1 + growth_rates[t-1])

    node.revenue = revenue_trajectory[-1]


def update_all(node):
    children = node.sub_units
    
    if not node.sub_units:  
        return node

    # Recursively optimize children first
    for child in node.sub_units:
        update_all(child)
    
    total_revenue = 0
    total_margin = 0
    volatilities = 0

    # Taking a weighted average for the level based on contribution ammounts
    for child in children:
        total_revenue += child.contribution  * child.revenue
        total_margin +=  child.contribution * child.margin

        if child.volatility is not None and child.volatility != 0:
            volatilities += child.contribution * child.volatility

    node.revenue = total_revenue
    node.volatility = volatilities
    node.margin = total_margin
    node.margin_dollars = node.revenue * node.margin

    return node


def run_monte_carlo_layer_5(strategy, years=5, target_layer=5):
    """
    Randomizes the revenue based on the segment level

    """

    queue = deque([(strategy, 0)])  

    while queue:
        node, level = queue.popleft()

        # If node is at the target layer, run Monte Carlo to simulate random walk modifying node in place
        if level == target_layer:
            monte_carlo_simulation(node, years)
         
        elif level < target_layer:
            # Continue traversal if below layer 5
            for child in node.sub_units:
                queue.append((child, level + 1))
    

    # update values
    update_all(strategy)
    return strategy

    

def run_strategy(strategy, years, n=100):
    """
    Runs Monte Carlo simulations for a given strategy.

    Parameters:
    - root: The root node of the strategy.
    - years: Number of years to simulate.
    - n: Number of Monte Carlo iterations.

    Returns:
    - A dictionary containing the results.
    """
    margin = []
    revenue = []

    for i in range(n): 
        temp_root = strategy.copy()

        # randomizes revenue based on trend data
        random_walk = run_monte_carlo_layer_5(temp_root, years)
        results = eval_optimizer(random_walk)

        margin.append(results['Margin Dollars'])
        revenue.append(results['Revenue'])

    return {
        "revenue": revenue,
        "margin": margin
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
        
        strategy = {'Name': strat_name}
        revenue = []
        margin = []
        for year in range(1, years+1):
            result = run_strategy(strat_root, year)

            revenue.append(result['revenue'])
            margin.append(result['margin'])

        strategy['revenue'] = revenue
        strategy['margin'] = margin
        all_results.append(strategy)


    return all_results

