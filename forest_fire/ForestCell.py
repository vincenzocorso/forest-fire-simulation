import numpy as np
from mesa import Agent


class ForestCell(Agent):
    """ A cell of the grid representing a forest area """
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.state = 0.0  # The current state of the cell
        self.next_state = None  # The next state of the cell

        self.rate_of_spread = 1.0  # measured in meters per second

        self.height = 0.0  # measured in meters
        self.height_factors = [[1.0 for _ in range(3)] for _ in range(3)]

        self.wind_component = 1

        self.rain_deficit = 0
        self.rain = 0

        self.is_burned = 0  # Indicate whether the cell is burned or not in the real wildfire (ground truth)

    def step(self):
        """ Calculate the next state of the cell using the given propagation rule """
        self.next_state = self.model.propagation_rule.apply(self)

    def advance(self):
        """ Update the current state of the cell """
        if self.state != self.next_state:
            print("Cell {} changed state from {} to {}".format(self.pos, self.state, self.next_state))

        self.state = self.next_state

    def get_height_factor(self, a, b):
        return self.height_factors[1 - b][a + 1]

    def update_height_factor(self, phi):
        """ Update the height factor matrix using the given slope function """
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
            a, b = np.array(neighbor.pos) - self.pos
            self.height_factors[1 - b][a + 1] = phi(self.height - neighbor.height, a, b, self.model.alpha)
