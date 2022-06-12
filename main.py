from collections import Counter
import gym
import gym_splendorm
import time
import copy

env = gym.make('gym_splendorm-v0')
def main():
    env.reset()

    while env.turn < 400:
        # env.render()
        o,a,done,t = env.step(env.players[env.turn % env.amount_player].action(env.dict_input))
        if done == True:
            break

    # env.render()
    # print('----------------------------------------------------------------------------------------------------')

    for i in range(env.players.__len__()):
        env.dict_input['Players'] = [env.players[(j+1)%env.amount_player] for j in range(env.amount_player-1)]
        env.players[i].action(env.dict_input)
        # env.render()
    
    for p in env.players:
        if p.infinity_card:
            # print(p.name)
            return p.name

    # print('None')
    return 'None'

a = time.time()
cnt = Counter(main() for i in range(1))
print(cnt)
b = time.time()
print(b-a)