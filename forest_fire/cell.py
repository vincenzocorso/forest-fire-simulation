import numpy as np
from mesa import Agent


class ForestCell(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.state = 0.0
        self.is_burned = 0
        self.next_state = None
        self.wind_component = 1
        self.rate_of_spread = 1.0  # meters per second
        self.height = 0.0  # meters
        self.rain = 0
        self.rain_deficit = 0
        self.height_factors = [[1.0 for _ in range(3)] for _ in range(3)]

    def step(self):
        self.next_state = self.model.propagation_rule.apply(self)

    def advance(self):
        if self.state != self.next_state:
            print("Cell " + str(self.pos) + " changed state from " + str(self.state) + " to " + str(self.next_state))

        self.state = self.next_state

    def get_height_factor(self, a, b):
        return self.height_factors[1 - b][a + 1]

    def update_height_factor(self, phi):
        for neighbor in self.model.grid.iter_neighbors(self.pos, moore=True):
            a, b = np.array(neighbor.pos) - self.pos
            self.height_factors[1 - b][a + 1] = phi(self.height - neighbor.height, a, b)
