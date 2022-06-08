from mesa import Model
from mesa.time import SimultaneousActivation
from .ConcurrentSimultaneousActivation import ConcurrentSimultaneousActivation
from mesa.space import SingleGrid
from .agent import ForestCell


class ForestFire(Model):
    def __init__(self, width, height):
        self.schedule = SimultaneousActivation(self)
        self.grid = SingleGrid(width, height, torus=False)

        self.cells = [[None for j in range(width)] for i in range(height)]
        self.setup_cells()

        self.cells[height // 2][width // 2].state = 1.0

        self.running = True

    def setup_cells(self):
        for (content, x, y) in self.grid.coord_iter():
            forest_cell = ForestCell((x, y), self)
            self.cells[x][y] = forest_cell
            self.grid.position_agent(forest_cell, x, y)
            self.schedule.add(forest_cell)

    def step(self):
        self.schedule.step()

