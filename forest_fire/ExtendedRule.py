import math
import numpy as np
from .PropagationRule import PropagationRule


class ExtendedRule(PropagationRule):
    """
        The extended model defined by the following paper:

        A. Hernández Encinas, L. Hernández Encinas, S. Hoya White, A. Martín del Rey, G. Rodríguez Sánchez,
        Simulation of forest fire fronts using cellular automata,
        Advances in Engineering Software,
        Volume 38, Issue 6,
        2007,
        Pages 372-378,
        ISSN 0965-9978,
        https://doi.org/10.1016/j.advengsoft.2006.09.002
    """

    def __init__(self, model):
        super().__init__(model)

        for (cell, _, _) in self.model.grid.coord_iter():
            cell.update_height_factor(self.h)

        self.wind_factors = [[1.0 for _ in range(3)] for _ in range(3)]

        # Define some support vectors to iterate the neighbors
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

    def apply(self, cell):
        not_burning_neighbour = True
        for (a, b) in self.v_adj+self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                if neighbor.state == 1.0:
                    not_burning_neighbour = False
        if cell.state == 1.0 or cell.rate_of_spread == 0.0 or not_burning_neighbour:
            return cell.state

        next_state = (cell.rate_of_spread / self.model.max_ros) * cell.state
        next_state += self.calculate_adj_term(cell)
        if cell.state < 1.0:
            next_state += self.calculate_diag_term(cell)
        # Apply a discretization function
        return self.g(next_state)

    def calculate_adj_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += self.get_wind_factor(a, b) * cell.get_height_factor(a, b) * neighbor.rate_of_spread * neighbor.state
        sum /= self.model.max_ros
        return sum

    def calculate_diag_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += self.get_wind_factor(a, b) * cell.get_height_factor(a, b) * neighbor.rate_of_spread * neighbor.state
        sum *= math.pi / (4 * self.model.max_ros ** 2)
        return sum

    @staticmethod
    def g(value):
        return 0.0 if value < 1.0 else 1.0

    @staticmethod
    def h(value):
        if value <= -50.0 or value >= 50.0:
            return 0.0

        if value < 0.0:
            return 2 - ((value / 20.71) + 1)**2

        return -(value / 50.0) + 1.0

    def get_wind_factor(self, a, b):
        return self.wind_factors[1 - b][a + 1]

