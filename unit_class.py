from typing import List, Optional

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
        self.min_contribution = max(min(min_contribution or 0.0, self.max_contribution), 0.0)
        
        self.contribution = (max_contribution + min_contribution) /2
        
        self.revenue = revenue
        self.margin = margin 

        # values dependent on contribution
        self.margin_dollars = None
        self.volatility = None

        self.min_trend = min_trend or 0.0
        self.max_trend = max_trend or 0.0

        self.sub_units: List["Unit"] = []  # Child units
        
        self._update_values()

    @property
    def contribution(self) -> float:
        return self._contribution

    @contribution.setter
    def contribution(self, value: float):
        """Ensures contribution is within min/max bounds."""
        self._contribution = max(min(value, self.max_contribution), self.min_contribution)

    def _update_values(self):

        children = self.sub_units
        if len(children) < 1:
            return 
        
        total_revenue = 0
        total_margin = 0
        volatilities = 0

        # Taking a weighted average for the level based on contribution ammounts
        for child in children:
            total_revenue += child.contribution  * child.revenue
            total_margin +=  child.contribution * child.margin

            if child.volatility is not None and child.volatility != 0:
                volatilities += child.contribution * child.volatility

        self.revenue = total_revenue
        self.volatility = volatilities
        self.margin = total_margin
        self.margin_dollars = self.revenue * self.margin

    def add_sub_unit(self, sub_unit: "Unit"):
        """Adds a sub-unit to this unit."""
        self.sub_units.append(sub_unit)

    def clear_sub_units(self):
        """Removes all sub-units."""
        self.sub_units.clear()

    def compute_totals(self):
        """Recursively calculate totals for the unit and its sub-units."""
        if self.sub_units:
            self.revenue = sum(sub.compute_totals() for sub in self.sub_units)
        return self.revenue or 0  # Ensure the function always returns a valid value

    def copy(self) -> "Unit":
        """Creates a deep copy of the unit and its sub-units."""
        new_unit = Unit(
            name=self.name,
            revenue=self.revenue,
            margin=self.margin,
            min_trend=self.min_trend,
            max_trend=self.max_trend,
            min_contribution=self.min_contribution,
            max_contribution=self.max_contribution
        )
        new_unit.sub_units = [child.copy() for child in self.sub_units]
        return new_unit
