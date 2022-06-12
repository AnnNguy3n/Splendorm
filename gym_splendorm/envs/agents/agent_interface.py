from gym_splendorm.envs.agents.agent_Ann import agent_Ann as p1
from gym_splendorm.envs.agents.agent_Ann import agent_Ann as p2
from gym_splendorm.envs.agents.agent_Ann import agent_Ann as p3
from gym_splendorm.envs.agents.agent_Ann import agent_Ann as p4

lst = [p1, p2, p3, p4]
lst_name = ['BOT1', 'BOT2', 'BOT3', 'BOT4']

list_players = [lst[i].Agent(lst_name[i]) for i in range(lst.__len__())]