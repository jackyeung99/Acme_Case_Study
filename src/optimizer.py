import numpy as np
from scipy.optimize import  minimize
# from hierarchy_tree import *

class ContributionOptimizer:
    def __init__(self,):
        pass

    def standardize(self, arr):
        """Standardizes an array to zero mean and unit variance."""
        std_dev = np.std(arr)
        return (arr - np.mean(arr)) / std_dev if std_dev > 0 else arr

    def compute_weighted_objective(self, contributions, children):
        """Computes the weighted objective function for optimization."""
        alpha, beta, gamma, delta = (
            self.weights["alpha"], self.weights["beta"], 
            self.weights["gamma"], self.weights["delta"]
        )

        revenues = self.standardize(np.array([child.revenue for child in children], dtype=np.float64))
        margins = self.standardize(np.array([child.margin for child in children], dtype=np.float64))
        growth = self.standardize(np.array([child.max_trend-child.min_trend for child in children]))
        volatilities = self.standardize(np.abs(growth)) 

        return np.sum(contributions * (alpha * revenues + beta * margins + gamma * growth - delta * volatilities))

    def objective(self, contributions, children):
        """Objective function to minimize."""
        return -self.compute_weighted_objective(contributions, children)

    def optimize_contributions(self, children):
        """Optimizes contribution percentages based on constraints."""
        x0 = [child.contribution for child in children]
        bounds = [(child.min_contribution, child.max_contribution) for child in children]
        constraint = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}

        result = minimize(
            self.objective, x0, args=(children,),
            constraints=[constraint], bounds=bounds, method='SLSQP'
        )

        if result.success:
            return result.x
        else:
            print("Warning: Optimization failed, returning initial values")
            return x0

    def optimize(self, hierarchy_tree, weights):
        """Creates a deep copy of the tree and optimizes it in a bottom-up manner."""
        self.weights = weights if weights else {
            "alpha": 0.5, "beta": 0.5, "gamma": 0.2, "delta": 0.1
        }

        def _optimize_recursive(sub_node):
            """Helper function to recursively optimize the copied tree."""
            if not sub_node.sub_units:  # Base case: No children
                return sub_node

            # Optimize children first
            for child in sub_node.sub_units:
                _optimize_recursive(child)

            if len(sub_node.sub_units) == 1:
                contributions = [1]
            else:
                contributions = self.optimize_contributions(sub_node.sub_units)

            # Assign new contributions
            for child, new_contribution in zip(sub_node.sub_units, contributions):
                child.contribution = new_contribution

            sub_node._update_values() 
            return sub_node

        return _optimize_recursive(hierarchy_tree)  
