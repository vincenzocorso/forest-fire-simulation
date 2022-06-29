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

    def __init__(self, width, height, alpha, c1, c2):
        """ Initialize the model """

        self.wildfire_name = "august250"
        self.alpha = alpha
        self.c1 = c1
        self.c2 = c2

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
        self.data_loader.load_rain(1)  # Load the rain data

        self.max_ros = self.get_max_ros()

        # Define the rule to use to update the state of each cell
        self.propagation_rule = OurRule(self)
        
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

    def step(self):
        """ Execute a step in the model """
        # Load the rain of the day
        if self.schedule.steps % 5 == 0:
            self.data_loader.load_rain(self.schedule.steps // 5 + 16)

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