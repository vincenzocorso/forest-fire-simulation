from abc import abstractmethod


class PropagationRule:
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def apply(self, cell):
        pass
