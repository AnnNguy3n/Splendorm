import numpy
import random
from ...base.player import Player
import json

class Agent(Player):
    def __init__(self, name):
        super().__init__(name)

    def reset(self):
        super().reset()
        self.history = []

    def action(self, dict_input):
        state = self.get_list_state(dict_input)
        if self.check_victory(state) == -1:
            list_index_action = self.get_list_index_action(state)
            action = random.choice(list_index_action)
            self.history.append((state, action))
            # print(state, action)
            return action
        else:
            with open(f'gym_splendorm/envs/agents/agent_Ann/exam_{self.name}.json', 'w') as f:
                f.write(
                    '[' + 
                    ',\n'.join(json.dumps(ii) for ii in self.history)
                    + ']'
                )

            return None