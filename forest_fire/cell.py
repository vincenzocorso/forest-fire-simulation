from mesa import Agent


class ForestCell(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)

        self.state = 0.0
        self.next_state = None

        self.rate_of_spread = 1.0

    def step(self):
        self.next_state = self.model.propagation_rule.apply(self)

    def advance(self):
        if self.state != self.next_state:
            print("Cell " + str(self.pos) + " changed state from " + str(self.state) + " to " + str(self.next_state))

        self.state = self.next_state
