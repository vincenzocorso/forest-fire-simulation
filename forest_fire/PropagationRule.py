from abc import abstractmethod


class PropagationRule:
    """ An abstract class for a propagation rule """
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def apply(self, cell):
        """ Return the next state of the cell """
        pass
