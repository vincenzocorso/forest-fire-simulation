from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid
from .ForestFire import ForestFire

# Define the width and the height of the map
width = 250
height = 250


def get_cell_color(cell):
    """ This method return the color of the cell """
    x, y = cell.pos
    if x == width // 2 and y == width // 2:  # Color the center of the map
        return "Yellow"
    if cell.state == 1.0 and not cell.is_burned:  # Color the cells that shouldn't have burned
        return "Purple"
    elif cell.state == 1.0:  # Color the cells correctly burned
        return "Black"
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
    "height": height
}
canvas_element = CanvasGrid(forest_fire_portrayal, width, height, width * 3, height * 3)

# Start the server
#server = ModularServer(ForestFire, [canvas_element], "Forest Fire", model_params)
alpha_values = [30, 45, 60, 75, 90]
c1_values = [0.125, 0.25, 0.5, 0.75, 1.5]
c2_values = [0.125, 0.25, 0.5, 0.75, 1.5]


for alpha in alpha_values:
    for c1 in c1_values:
        for c2 in c2_values:
            max_f1 = -1
            max_pr = -1
            max_rec = -1
            step_f1 = 0
            step_pr = 0
            step_rec = 0
            firemodel = ForestFire(250,250, alpha, c1, c2)
            for i in range(50):
                f1, precision, recall = firemodel.step()
                if f1 > max_f1:
                    max_f1 = f1
                    step_f1 = i
                if precision > max_pr:
                    max_pr = precision
                    step_pr = i
                if recall > max_rec:
                    max_rec = recall
                    step_rec = i
            with open('data_log.txt', 'a') as f:
                f.writelines(["Model alpha={}, c1={}, c2={}, f1={} step={}, prec={} step={}, rec={} step={}\n".format(alpha,c1,c2,max_f1,step_f1,max_pr,step_pr,max_rec,step_rec)])
            