import math


class SlopeFunctions:
    """ This class contains some functions to calculate slope coefficients """

    @staticmethod
    def h(value, a, b):
        if value <= -50.0 or value >= 50.0:
            return 0.0

        if value < 0.0:
            return 2 - ((value / 20.71) + 1) ** 2

        return -(value / 50.0) + 1.0

    @staticmethod
    def h2(value, a, b):
        value = -value
        if value <= -100.0 or value >= 100.0:
            return 0
        if value <= 0.0:
            return (1 / 100) * value + 1
        if value <= 50:
            return (1 / 50) * value + 1

        return (-2 / 50) * (value - 2) + 2

    @staticmethod
    def slope_h(value, a, b):
        slope = math.atan(value / 496)
        if value <= 0:
            return -1 / (math.pi / 4) * slope + 1
        if slope <= math.pi / 4:
            return 1 / (math.pi / 4) * slope + 1

        return -2 / (1.39626 - math.pi / 4) * (slope - math.pi / 4) + 2

    @staticmethod
    def slope_h2(value, a, b, tmp):
        value = -value
        alpha = tmp
        beta = 1.0
        if a != 0 and b == 0:  # horizontal
            length = 656
        elif a == 0 and b != 0:  # vertical
            length = 812
        else:  # diagonal
            length = 1044

        length *= beta
        theta = math.atan(value / length)
        return math.exp(alpha * theta)
