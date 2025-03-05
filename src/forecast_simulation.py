from collections import deque
import numpy as np
from src.helpers import *
from src.optimizer import *

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

    mu = (node.min_trend + node.max_trend) / 2
    sigma = (np.abs(node.max_trend - node.min_trend)) / 4  # 95% confidence range

    # Generate a single trajectory of growth rates
    # growth_rates = np.random.normal(loc=mu, scale=sigma, size=years)
    growth_rates = np.random.lognormal(mean=mu, sigma=sigma, size=years)

    growth_rates = np.clip(growth_rates, node.min_trend, node.max_trend)

    revenue_trajectory = np.zeros(years+1)
    revenue_trajectory[0] = node.revenue  

    # Simulate revenue using random walk
    dt = 1
    for t in range(1, years+1):
        epsilon = np.random.normal(0, 1) 
        revenue_trajectory[t] = revenue_trajectory[t-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * epsilon)

    node.revenue = revenue_trajectory[-1]



def run_monte_carlo(strategy, years=5, target_layer=5):
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
        random_walk = run_monte_carlo(temp_root, years)
        results = eval_optimizer(random_walk)

        margin.append(results['Profit'])
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

