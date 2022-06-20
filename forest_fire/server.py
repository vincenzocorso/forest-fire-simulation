from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from .model import ForestFire

width = 250
height = 250

is_burned = []
with open("data/woolsey_new/burned_mask.csv", "r") as file:
    for line in file:
        line = line.split(",")
        line = [float(i) for i in line]
        is_burned.append(line)


def get_cell_color(cell):
    x, y = cell.pos
    if x == width // 2 and y == width // 2:
        return "Yellow"
    if cell.state == 1.0 and not is_burned[height - 1 - y][x]:
         return "Purple"
    elif cell.state == 1.0:
        return "Black"
    elif 0.5 < cell.state < 1.0:
        return "Red"
    elif is_burned[height - 1 - y][x]:
         return "Green"
    elif cell.state == 0.0:
        return "White"


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
canvas_element = CanvasGrid(forest_fire_portrayal, width, height, width * 3, height * 3)

server = ModularServer(ForestFire, [canvas_element], "Forest Fire", model_params)
