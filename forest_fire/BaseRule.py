import numpy as np
from .PropagationRule import PropagationRule


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

        self.wind_factors = [[1.0 for _ in range(3)] for _ in range(3)]
        self.height_factors = [[1.0 for _ in range(3)] for _ in range(3)]

        # Define some support vectors to iterate the neighbors
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

    def apply(self, cell):
        if cell.state == 1.0 or cell.rate_of_spread == 0.0:
            return cell.state

        next_state = cell.state
        next_state += self.calculate_adj_term(cell)
        if cell.state < 1.0:
            next_state += self.calculate_diag_term(cell)
        return min(1.0, next_state)

    def calculate_adj_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                sum += self.get_wind_factor(a, b) * self.get_height_factor(a, b) * self.model.get_cell(x, y).state
        return sum

    def calculate_diag_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                sum += self.get_wind_factor(a, b) * self.get_height_factor(a, b) * self.model.get_cell(x, y).state
        sum *= 0.83
        return sum

    def get_wind_factor(self, a, b):
        return self.wind_factors[1 - b][a + 1]

    def get_height_factor(self, a, b):
        return self.height_factors[1 - b][a + 1]
