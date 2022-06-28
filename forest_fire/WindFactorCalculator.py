import math
import random
import numpy as np

# Define some support vectors to iterate the neighbors
v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])

# Define some support vectors to iterate cell angles
ang_adj = np.array([180, 270, 0, 90])
ang_diag = np.array([135, 225, 315, 45])


class WindFactorCalculator:
    @staticmethod
    def compute_wind_factor(model, cell):
        """ Compute the wind factors """
        gust_prob = 0.1  # The probability of gust of wind
        c1 = 0.25
        c2 = 0.75

        wind_angle = model.wind[16 + (model.schedule.steps // 5)][2]
        if random.random() < gust_prob:
            wind_speed = model.wind[16 + (model.schedule.steps // 5)][0] / 3.6
        else:
            wind_speed = model.wind[16 + (model.schedule.steps // 5)][1] / 3.6
        fire_angle = WindFactorCalculator.get_fire_direction(model, cell)
        if fire_angle == -1:
            return 0
        angle_difference = abs(wind_angle - fire_angle) % 360
        if angle_difference > 180:
            angle_difference = 360 - angle_difference
        ft = math.exp(wind_speed * c2 * (math.cos(math.radians(angle_difference)) - 1))
        return math.exp(c1 * wind_speed) * ft

    @staticmethod
    def get_fire_direction(model, cell):
        sum_ang = 0
        sum_states = 0
        for index, (a, b) in enumerate(v_adj):
            x, y = cell.pos + np.array((a, b))
            if not model.grid.out_of_bounds((x, y)):
                neighbor = model.get_cell(x, y)
                ang = ang_adj[index]
                sum_ang += ang * neighbor.state
                sum_states += neighbor.state

        for index, (a, b) in enumerate(v_diag):
            x, y = cell.pos + np.array((a, b))
            if not model.grid.out_of_bounds((x, y)):
                neighbor = model.get_cell(x, y)
                ang = ang_diag[index]
                sum_ang += ang * neighbor.state
                sum_states += neighbor.state
        if sum_states == 0:
            return -1
        return sum_ang / sum_states
