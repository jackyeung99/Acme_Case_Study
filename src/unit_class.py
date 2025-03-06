from typing import List, Optional
import numpy as np
import pandas as pd
from collections import deque

class Unit:
    def __init__(self, 
                 name: Optional[str] = None, 
                 revenue: Optional[float] = 0.0, 
                 margin: Optional[float] = 0.0, 
                 min_trend: Optional[float] = None, 
                 max_trend: Optional[float] = None, 
                 min_contribution: Optional[float] = 0.0, 
                 max_contribution: Optional[float] = 1.0):
        
        self.name = name
        
        # Contribution Bounds
        self.max_contribution = max(min(max_contribution, 1.0), 0.0) if max_contribution is not None else 1.0
        self.min_contribution = max(min(min_contribution, self.max_contribution), 0.0)
        
        self._contribution = (self.max_contribution + self.min_contribution) / 2
        
        self.revenue = revenue
        self.margin = margin 

        # Values dependent on contribution
        self.margin_dollars = None
        self.volatility = None

        self.min_trend = min_trend or 0.0
        self.max_trend = max_trend or 0.0

        self.sub_units: List["Unit"] = [] 
    
    def update_parameters(self, parameters):

        if 'max_trend' in parameters:
            self.max_trend = parameters['max_trend']
        if 'min_trend' in parameters:
            self.min_trend = parameters['min_trend']
        

    @property
    def contribution(self) -> float:
        return self._contribution

    @contribution.setter
    def contribution(self, value: float):
        """Ensures contribution is within min/max bounds."""
        self._contribution = max(min(value, self.max_contribution), self.min_contribution)

    def add_sub_unit(self, sub_unit: "Unit"):
        """Adds a sub-unit to this unit."""
        self.sub_units.append(sub_unit)

    def clear_sub_units(self):
        """Removes all sub-units."""
        self.sub_units.clear()


    def _update_values(self):
        """Recursively update revenue, margin, and volatility."""
        if not self.sub_units:
            return

        total_revenue, total_margin, volatilities = 0, 0, 0

        for child in self.sub_units:

            total_revenue += child.contribution * child.revenue
            total_margin += child.contribution * child.margin

            if child.volatility is not None and child.volatility != 0:
                volatilities += child.contribution * child.volatility

        self.revenue = total_revenue
        self.margin = total_margin
        self.volatility = volatilities
        self.margin_dollars = self.revenue * self.margin

    