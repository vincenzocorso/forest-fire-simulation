from mesa import Agent
from .KTModel import KTModel
from .ExtendedModel import ExtendedModel


class ForestCell(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.state = 0.0
        self.next_state = None

        self.fire_spread_model = ExtendedModel(model, self)

    def step(self):
        self.next_state = self.fire_spread_model.apply()

    def advance(self):
        if self.state != self.next_state:
            print("Cell " + str(self.pos) + " changed state from " + str(self.state) + " to " + str(self.next_state))

        self.state = self.next_state
