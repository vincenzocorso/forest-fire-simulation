import numpy as np
from .PropagationRule import PropagationRule
from .SlopeFunctions import SlopeFunctions
from .WindFactorCalculator import WindFactorCalculator


class BaseRule(PropagationRule):
    """
        The base model defined by the following paper:

        Ioannis Karafyllidis, Adonios Thanailakis,
        A model for predicting forest fire spreading using cellular automata,
        Ecological Modelling,
        Volume 99, Issue 1,
        1997,
        Pages 87-97,
        ISSN 0304-3800,
        https://doi.org/10.1016/S0304-3800(96)01942-4
    """

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
        cell.wind_component = WindFactorCalculator.compute_wind_factor(self.model, cell)

        # Calculate the next state using the formula given in the paper
        next_state = cell.state
        next_state += self.calculate_adj_term(cell)
        if next_state < 1.0:
            next_state += self.calculate_diag_term(cell)

        # Cap the result to 1.0
        return min(1.0, next_state)

    def calculate_adj_term(self, cell):
        """ Calculate the adjacent sum term of the formula """
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.state
        return sum

    def calculate_diag_term(self, cell):
        """ Calculate the diagonal sum term of the formula """
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.state
        sum *= 0.83
        return sum
