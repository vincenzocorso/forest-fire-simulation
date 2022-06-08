from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from .model import ForestFire

width = 100
height = 100

def get_cell_color(cell):
    x, y = cell.pos
    if x == width // 2 and y == width // 2:
        return "Green"
    elif cell.state == 0.0:
        return "White"
    elif cell.state == 1.0:
        return "Black"
    else:
        return "Red"


def forest_fire_portrayal(cell):
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

model_params = {
    "width": width,
    "height": height
}
canvas_element = CanvasGrid(forest_fire_portrayal, width, height, width * 5, height * 5)

server = ModularServer(ForestFire, [canvas_element], "Forest Fire", model_params)
