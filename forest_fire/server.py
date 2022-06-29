import os
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.UserParam import UserSettableParameter
from .ForestFire import ForestFire

# Define the width and the height of the map
width = 250
height = 250

scenarios = [item for item in os.listdir("./data") if os.path.isdir(os.path.join("./data", item))]

def get_cell_color(cell):
    """ This method return the color of the cell """
    x, y = cell.pos
    if x == width // 2 and y == width // 2:  # Color the center of the map
        return "Yellow"
    if cell.state == 1.0 and not cell.is_burned:  # Color the cells that shouldn't have burned
        return "Purple"
    elif cell.state == 1.0:  # Color the cells correctly burned
        return "Black"
    elif 0.0 < cell.state < 1.0:
        return "Red"
    elif cell.is_burned:  # Color the cells burned during the wildfire, but not in the simulation
        return "Green"
    else:  # The default color is white
        return "White"


def forest_fire_portrayal(cell):
    """ This method return the style of the cell """
    (x, y) = cell.pos
    portrayal = {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": x,
        "y": y,
        "Color": get_cell_color(cell)
    }
    return portrayal


# Create a canvas grid
model_params = {
    "width": width,
    "height": height,
    "propagation_rule": UserSettableParameter("choice", "PropagationRule", value="OurRule", choices=["OurRule", "BaseRule", "ExtendedRule"]),
    "scenario": UserSettableParameter("choice", "Scenario", value=scenarios[0], choices=scenarios)
}
canvas_element = CanvasGrid(forest_fire_portrayal, width, height, width * 3, height * 3)

# Start the server
server = ModularServer(ForestFire, [canvas_element], "Forest Fire", model_params)
