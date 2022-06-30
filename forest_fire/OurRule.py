import math
import numpy as np
from .PropagationRule import PropagationRule
from .SlopeFunctions import SlopeFunctions
from .WindFactorCalculator import WindFactorCalculator
from .RainFactorCalculator import RainFactorCalculator


class OurRule(PropagationRule):
    """ The extended model defined by our project: """

    def __init__(self, model):
        super().__init__(model)

        # Update height factors using a slope function
        for (cell, _, _) in self.model.grid.coord_iter():
            cell.update_height_factor(SlopeFunctions.slope_h2)

        # Define some support vectors to iterate the neighbors
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

    def apply(self, cell):
        """ Calculate the next state of the cell """
        if cell.state == 1.0 or cell.rate_of_spread == 0.0:
            return cell.state

        # Compute the wind component
        cell.wind_component = WindFactorCalculator.compute_wind_factor(self.model, cell, self.model.c1, self.model.c2)

        spread_reduction = 1 - cell.rain_deficit

        # Calculate the next state using the formula given in the paper
        next_state = (cell.rate_of_spread * spread_reduction / self.model.max_ros) * cell.state
        next_state += self.calculate_adj_term(cell)
        if next_state < 1.0:
            next_state += self.calculate_diag_term(cell)

        # Apply the rain factor
        next_state = RainFactorCalculator.compute_rain_factor(cell, next_state)

        # Cap the result
        if 0.0 < next_state < 0.001:
            return 0.0
        else:
            return min(1, next_state)

    def calculate_adj_term(self, cell):
        """ Calculate the adjacent sum term of the formula """
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                spread_reduction = 1 - neighbor.rain_deficit
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread * spread_reduction * neighbor.state
        sum /= self.model.max_ros
        return sum

    def calculate_diag_term(self, cell):
        """ Calculate the diagonal sum term of the formula """
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                spread_reduction = 1 - neighbor.rain_deficit
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread**2 * spread_reduction * neighbor.state
        sum *= math.pi / (4 * self.model.max_ros ** 2)
        return sum
