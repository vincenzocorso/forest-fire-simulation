import math
import numpy as np
from .FireSpreadModel import FireSpreadModel


class ExtendedModel(FireSpreadModel):
    def __init__(self, model, agent):
        super().__init__(model, agent)
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

        # self.wind_matrix = [[1.0 for j in range(3)] for i in range(3)]
        self.wind_matrix = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ]
        self.height_matrix = [[1.0 for j in range(3)] for i in range(3)]

    def apply(self):
        next_state = self.agent.state
        if self.agent.state != 1.0:
            for (a, b) in self.v_adj:
                i, j = self.agent.pos + np.array((a, b))
                if not self.model.grid.out_of_bounds((i, j)):
                    adj_cell = self.model.cells[i][j]
                    next_state += self.get_wind_term(a, b) * self.get_height_term(a, b) * adj_cell.state

            diag_sum = 0.0
            for (a, b) in self.v_diag:
                i, j = self.agent.pos + np.array((a, b))
                if not self.model.grid.out_of_bounds((i, j)):
                    diag_cell = self.model.cells[i][j]
                    diag_sum += self.get_wind_term(a, b) * self.get_height_term(a, b) * diag_cell.state
            next_state += (math.pi / 4) * diag_sum

        return min(1.0, next_state)

    def get_wind_term(self, a, b):
        return self.wind_matrix[a + 1][1 - b]

    def get_height_term(self, a, b):
        return self.wind_matrix[a + 1][1 - b]
