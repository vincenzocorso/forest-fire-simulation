import csv
from mesa import Model
from mesa.time import SimultaneousActivation
from .ConcurrentSimultaneousActivation import ConcurrentSimultaneousActivation
from mesa.space import SingleGrid
from .cell import ForestCell
from .ExtendedRule import ExtendedRule
from .BaseRule import BaseRule


class ForestFire(Model):
    """ Define the Forest Fire Model and its parameters"""

    def __init__(self, width, height):
        """ Initialize the model """

        # Define how the agents' behaviour will be scheduled
        self.schedule = SimultaneousActivation(self)
        self.wind = []

        # Define the type of space
        self.width = width
        self.height = height
        self.grid = SingleGrid(self.width, self.height, torus=False)

        # Initialize each cell and set the initial state
        # The initial state is a circle of radius 10
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.setup_cells()
        #hopkins fire
        starting_point = (105, 170)
        self.draw_circle(starting_point, 1)
        #doe fire
        starting_point2 = (160, 102)
        self.draw_circle(starting_point2, 5)
        #hulls grave
        starting_point3 = (130, 70)
        self.draw_circle(starting_point3, 1)
        #hulls grave
        starting_point4 = (140, 130)
        self.draw_circle(starting_point4, 2)


        # Load the rates of spread of each cell
        self.load_rates_of_spread()
        self.max_ros = self.get_max_ros()

        # Load the height of each cell
        self.load_heights()
        self.load_wind()
        self.load_rain(1)

        # Define the rule to use to update the state of each cell
        self.propagation_rule = ExtendedRule(self)

        self.running = True

    def setup_cells(self):
        """ Setup the grid """
        for (_, x, y) in self.grid.coord_iter():
            forest_cell = ForestCell((x, y), self)
            self.set_cell(x, y, forest_cell)
            self.grid.position_agent(forest_cell, x, y)
            self.schedule.add(forest_cell)

    def draw_circle(self, center, radius):
        """ Draw a circle at the given center """
        x0, y0 = center
        for (cell, x, y) in self.grid.coord_iter():
            if (x - x0)**2 + (y - y0)**2 <= radius**2:
                self.get_cell(x, y).state = 1.0

    def get_cell(self, x, y):
        """ Return the cell at the given position. The coordinate (x=0, y=0) indicate the bottom left corner """
        return self.cells[self.height - 1 - y][x]

    def set_cell(self, x, y, cell):
        """ Set the cell at the given position. The coordinate (x=0, y=0) indicate the bottom left corner """
        self.cells[self.height - 1 - y][x] = cell

    def get_max_ros(self):
        """ Return the maximum rate of spread in the grid """
        max_ros = 0.0
        for (cell, x, y) in self.grid.coord_iter():
            max_ros = max(max_ros, cell.rate_of_spread)
        return max_ros

    def load_rates_of_spread(self):
        with open("data/august250/spread_component.csv", "r") as file:
            rates_of_spread = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                rates_of_spread.append(line)

            for (cell, x, y) in self.grid.coord_iter():
                cell.rate_of_spread = rates_of_spread[self.height - 1 - y][x]

    def load_heights(self):
        with open("data/august250/elevation.csv", "r") as file:
            heights = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                heights.append(line)

            for (cell, x, y) in self.grid.coord_iter():
                cell.height = heights[self.height - 1 - y][x]

    def load_wind(self):
        with open("data/august250/wind.csv", "r") as file:
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                self.wind.append(line)

    def load_rain(self, day):

        with open("data/august250/rain/rain"+str(int(day))+".csv" , "r") as file:
            rain = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                rain.append(line)

            for (cell, x, y) in self.grid.coord_iter():
                cell.rain = rain[self.height - 1 - y][x] / 12

    def step(self):
        """ Execute a step in the model """
        if self.schedule.steps % 5 == 0:
            self.load_rain(self.schedule.steps/5 + 16)
        self.schedule.step()
