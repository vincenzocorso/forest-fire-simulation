import os.path


class DataLoader:
    """ Load scenarios data from csv file """
    def __init__(self, model):
        self.model = model

    def load_starting_points(self):
        with open("data/{}/starting_points.csv".format(self.model.wildfire_name), "r") as file:
            for line in file:
                line = line.split(",")
                starting_point = (float(line[0]), float(line[1]))
                radius = float(line[2])
                point_name = line[3].strip()
                self.model.draw_circle(starting_point, radius)
                print("Loaded fire at {} (radius: {}, name: {})".format(starting_point, radius, point_name))
        print("All starting points have been loaded")

    def load_burned_map(self):
        if os.path.exists("data/{}/burned_mask.csv".format(self.model.wildfire_name)):
            with open("data/{}/burned_mask.csv".format(self.model.wildfire_name), "r") as file:
                is_burned = []
                for line in file:
                    line = line.split(",")
                    line = [float(i) for i in line]
                    is_burned.append(line)

                for (cell, x, y) in self.model.grid.coord_iter():
                    cell.is_burned = is_burned[self.model.height - 1 - y][x]
            print("The burned map has been loaded")

    def load_rates_of_spread(self):
        with open("data/{}/spread_component.csv".format(self.model.wildfire_name), "r") as file:
            rates_of_spread = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                rates_of_spread.append(line)

            for (cell, x, y) in self.model.grid.coord_iter():
                cell.rate_of_spread = rates_of_spread[self.model.height - 1 - y][x]
        print("The rates of spread have been loaded")

    def load_heights(self):
        with open("data/{}/elevation.csv".format(self.model.wildfire_name), "r") as file:
            heights = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                heights.append(line)

            for (cell, x, y) in self.model.grid.coord_iter():
                cell.height = heights[self.model.height - 1 - y][x]
        print("The elevation map has been loaded")

    def load_wind(self):
        with open("data/{}/wind.csv".format(self.model.wildfire_name), "r") as file:
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                self.model.wind.append(line)
        print("The wind map has been loaded")

    def load_rain(self, day):
        with open("data/{}/rain/rain{}.csv".format(self.model.wildfire_name, day), "r") as file:
            rain = []
            for line in file:
                line = line.split(",")
                line = [float(i) for i in line]
                rain.append(line)

            for (cell, x, y) in self.model.grid.coord_iter():
                cell.rain = rain[self.model.height - 1 - y][x]
        print("The rain data at day {} has been loaded".format(day))

    def load_starting_day(self):
        with open("data/{}/starting_day.csv".format(self.model.wildfire_name), "r") as file:
            self.model.starting_day = int(file.read())
