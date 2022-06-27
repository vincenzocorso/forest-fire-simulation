import math
import numpy as np
import random
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
            cell.update_height_factor(self.slope_h2)

        self.wind_factors = [[1.0 for _ in range(3)] for _ in range(3)]

        # Define some support vectors to iterate the neighbors
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

        # Define some support vectors to iterate cell angles
        self.ang_adj = np.array([180, 270, 0, 90])
        self.ang_diag = np.array([135, 225, 315, 45])

    def apply(self, cell):
        if cell.state == 1.0 or cell.rate_of_spread == 0.0:
            return cell.state

        cell.wind_component = self.compute_wind_factor(cell)
        next_state = (cell.rate_of_spread / self.model.max_ros) * cell.state
        next_state += self.calculate_adj_term(cell)
        if next_state < 1.0:
            next_state += self.calculate_diag_term(cell)

        return self.g(next_state)

    def calculate_adj_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread * neighbor.state
        sum /= self.model.max_ros
        return sum

    def calculate_diag_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread**2 * neighbor.state
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
            return 2 - ((value / 20.71) + 1) ** 2

        return -(value / 50.0) + 1.0

    @staticmethod
    def h2(value):
        value = -value
        if value <= -100.0 or value >= 100.0:
            return 0
        if value <= 0.0:
            return (1 / 100) * value + 1
        if value <= 50:
            return (1 / 50) * value + 1

        return (-2 / 50) * (value - 2) + 2

    @staticmethod
    def slope_h(value):
        slope = math.atan(value / 496)
        if value <= 0:
            return -1 / (math.pi / 4) * slope + 1
        if slope <= math.pi / 4:
            return 1 / (math.pi / 4) * slope + 1

        return -2 / (1.39626 - math.pi / 4) * (slope - math.pi / 4) + 2

    @staticmethod
    def slope_h2(value, a, b):
        value = -value
        alpha = 62.5
        beta = 1.0
        if a != 0 and b == 0:  # horizontal
            length = 656
        elif a == 0 and b != 0:  # vertical
            length = 812
        else:  # diagonal
            length = 1044

        length *= beta
        O = math.atan(value / length)
        return math.exp(alpha * O)

    def compute_wind_factor(self, cell):
        gust_prob = 0.1
        c1 = 0.75
        c2 = 0.75

        wind_angle = self.model.wind[16 + (self.model.schedule.steps // 5)][2]
        if random.random() < gust_prob:
            wind_speed = self.model.wind[16 + (self.model.schedule.steps // 5)][0] / 3.6
        else:
            wind_speed = self.model.wind[16 + (self.model.schedule.steps // 5)][1] / 3.6
        fire_angle = self.get_fire_direction(cell)
        if fire_angle == -1:
            return 0
        angle_difference = abs(wind_angle - fire_angle) % 360
        if angle_difference > 180:
            angle_difference = 360 - angle_difference
        ft = math.exp(wind_speed * c2 * (math.cos(math.radians(angle_difference)) - 1))
        return math.exp(c1 * wind_speed) * ft

    def get_fire_direction(self, cell):
        sum_ang = 0
        sum_states = 0
        for index, (a, b) in enumerate(self.v_adj):
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                ang = self.ang_adj[index]
                sum_ang += ang * neighbor.state
                sum_states += neighbor.state

        for index, (a, b) in enumerate(self.v_diag):
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                ang = self.ang_diag[index]
                sum_ang += ang * neighbor.state
                sum_states += neighbor.state
        if sum_states == 0:
            return -1
        return sum_ang / sum_states
