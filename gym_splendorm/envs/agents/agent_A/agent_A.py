import numpy
import random
from ...base.player import Player


class Agent(Player):
    def __init__(self, name):
        super().__init__(name)
        self.reset()

    def reset(self):
        super().reset()

    def action(self, dict_input):
        list_index_action = self.get_list_index_action(self.get_list_state(dict_input))
        action = random.choice(list_index_action)
        return action