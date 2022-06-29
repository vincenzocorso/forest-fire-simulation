import math
from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import SingleGrid
from .ForestCell import ForestCell
from .DataLoader import DataLoader
from .BaseRule import BaseRule
from .ExtendedRule import ExtendedRule
from .OurRule import OurRule


class ForestFire(Model):
    """ Define the Forest Fire Model and its parameters"""

    def __init__(self, width, height, propagation_rule, scenario):
        """ Initialize the model """

        self.wildfire_name = scenario
        self.starting_day = 0

        # Define how the agents' behaviour will be scheduled
        self.schedule = SimultaneousActivation(self)

        # Define the space type
        self.width = width
        self.height = height
        self.grid = SingleGrid(self.width, self.height, torus=False)

        # Initialize each cell and set the initial state
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.setup_cells()

        self.wind = []

        # Load wildfire data
        self.data_loader = DataLoader(self)
        self.data_loader.load_starting_points()  # Load the wildfire starting points
        self.data_loader.load_burned_map()  # Load the burned map
        self.data_loader.load_rates_of_spread()  # Load the rates of spread of each cell
        self.data_loader.load_heights()  # Load the height of each cell
        self.data_loader.load_wind()  # Load the wind data
        self.data_loader.load_starting_day()  # Load the starting day

        print("The starting day is {}".format(self.starting_day))

        self.max_ros = self.get_max_ros()
        print("The maximum rate of spread is {} m/s".format(self.max_ros))

        self.cell_length = 734  # Length of a cell in meters
        print("The cell length is {} m".format(self.cell_length))

        self.seconds_per_step = self.cell_length // self.max_ros
        print("In the simulation 1 step is equivalent to {} seconds".format(self.seconds_per_step))

        self.seconds_per_day = 86400
        self.steps_per_day = math.ceil(self.seconds_per_day / self.seconds_per_step)
        print("In the simulation 1 day is equivalent to {} steps".format(self.steps_per_day))

        # Define the rule to use to update the state of each cell
        self.propagation_rule = self.get_propagation_rule(propagation_rule)

        self.running = True

    def get_propagation_rule(self, propagation_rule):
        """ Return the propagation rule object """
        if propagation_rule == "BaseRule":
            return BaseRule(self)
        elif propagation_rule == "ExtendedRule":
            return ExtendedRule(self)
        elif propagation_rule == "OurRule":
            return OurRule(self)
        else:
            raise RuntimeError("Rule not found")

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
            if (x - x0) ** 2 + (y - y0) ** 2 <= radius ** 2:
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

    def get_days_elapsed(self):
        return self.schedule.steps // self.steps_per_day

    def step(self):
        """ Execute a step in the model """
        # Load the daily rain
        if self.schedule.steps % self.steps_per_day == 0:
            self.data_loader.load_rain(self.starting_day + self.get_days_elapsed())

        self.schedule.step()

        return self.compute_metric()

    def compute_metric(self):
        tp = 0
        tn = 0
        fp = 0
        fn = 0
        for i in range(250):
            for j in range (250):
                cell = self.get_cell(i,j)
                if cell.is_burned and cell.state == 1:
                    tp += 1
                elif cell.is_burned and cell.state != 1:
                    fn += 1
                elif not cell.is_burned and cell.state == 1:
                    fp += 1
                elif not cell.is_burned and cell.state != 1:
                    tn += 1

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f1 = 2 * 1/(1/precision + 1/recall)
        return f1, precision, recall
