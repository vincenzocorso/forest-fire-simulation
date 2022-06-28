import math
import numpy as np
import random
from .PropagationRule import PropagationRule


class OurRule(PropagationRule):
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
        #self.wind_factors = [[0.8, 1.4, 1.7], [0.6, 1, 1.4], [0.3, 0.6, 1.2]]
        # Define some support vectors to iterate the neighbors
        self.v_adj = np.array([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.ang_adj = np.array([180, 270, 0, 90])
        self.v_diag = np.array([(-1, 1), (1, 1), (1, -1), (-1, -1)])
        self.ang_diag = np.array([135, 225, 315, 45])

    def apply(self, cell): 
        if cell.state == 1.0 or cell.rate_of_spread == 0.0:
            return cell.state
        cell.wind_component = self.compute_wind_factor(cell)
        spread_reduction = 1 - cell.rain_deficit
        next_state = (cell.rate_of_spread * spread_reduction / self.model.max_ros) * cell.state
        next_state += self.calculate_adj_term(cell)
        if next_state < 1.0:
            next_state += self.calculate_diag_term(cell)

        next_state = self.compute_rain_component(cell, next_state)
        # Apply a discretization function
        if next_state > 0 and next_state < 0.001:
            next_state = 0
        return min(1,next_state)
        #return self.g(next_state)

    def calculate_adj_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_adj:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                spread_reduction = 1 - neighbor.rain_deficit
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread * spread_reduction * neighbor.state
        sum /= self.model.max_ros
        return sum

    def calculate_diag_term(self, cell):
        sum = 0.0
        for (a, b) in self.v_diag:
            x, y = cell.pos + np.array((a, b))
            if not self.model.grid.out_of_bounds((x, y)):
                neighbor = self.model.get_cell(x, y)
                spread_reduction = 1 - neighbor.rain_deficit
                sum += cell.wind_component * cell.get_height_factor(a, b) * neighbor.rate_of_spread**2 * spread_reduction * neighbor.state
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



    @staticmethod
    def h2(value):
        value = -value
        if value <= -100.0 or value >= 100.0:
            return 0
        if value <= 0.0:
            return (1/100)*value + 1
        if value <= 50:
            return (1/50)*value + 1
        
        return (-2/50)*(value - 2) + 2

    @staticmethod
    def slope_h(value):
        slope = math.atan(value/496)
        if value <= 0:
            return -1/(math.pi/4) * slope + 1
        if slope <= math.pi/4:
            return 1/(math.pi/4) * slope + 1
        
        return -2/(1.39626 - math.pi/4) * (slope - math.pi/4) + 2

    @staticmethod
    def slope_h2(value, a, b):
        value = -value
        alpha = 30.0
        beta = 1.0
        #horizontal
        if a != 0 and b == 0:
            lenght = 656
        #vertical
        elif a == 0 and b != 0:
            lenght = 812
        #diagonal
        else:
            lenght = 1044
    
        lenght *= beta
        O = math.atan(value/lenght) 
        return math.exp(alpha*O)

    def get_wind_factor(self, a, b):
        return self.wind_factors[1 - b][a + 1]
    
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
        return sum_ang/sum_states

    def compute_wind_factor(self,cell):
        gust_prob = 0.1
        c1 = 0.1
        c2 = 1.25
        wind_angle = self.model.wind[16 + (self.model.schedule.steps // 5) ][2]
        if random.random() < gust_prob:
            wind_speed = self.model.wind[16 + (self.model.schedule.steps // 5) ][0] / 3.6
        else:
            wind_speed = self.model.wind[16 + (self.model.schedule.steps // 5) ][1] / 3.6
        fire_angle = self.get_fire_direction(cell)
        if fire_angle == -1:
            return 0
        angle_difference = abs(wind_angle - fire_angle) % 360
        if angle_difference > 180:
            angle_difference = 360 - angle_difference
        ft = math.exp(wind_speed * c2 * (math.cos(math.radians(angle_difference)) - 1))
        return math.exp(c1 * wind_speed) * ft

     # rain component:
    # if raining and burning -> decrease burning state
    # if raining and not burning (nor burned) -> decrease temporarily sc (sc_deficit)
    # if not raining and not burning -> halves sc_deficit (soil is drying)
    def compute_rain_component(self, cell, state):
        if cell.rain > 0:
            if state > 0:
                return state*self.rain_suppression(cell)
            else:
                cell.rain_deficit = self.rain_sc_reduction(cell)
                return state
        else:
            update_deficit = cell.rain_deficit * 0.5
            if update_deficit < 0.01:
                update_deficit = 0
            cell.rain_deficit = update_deficit
            return state

    def rain_suppression(self, cell):
        return 1 - max(min(0.8,(0.0242424242424*cell.rain) - 0.0484848484848), 0)
        
    def rain_sc_reduction(self,cell):
        return max(min(0.8,0.12*cell.rain), 0)