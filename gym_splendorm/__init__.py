from gym.envs.registration import register

register(
    id='gym_splendorm-v0',    
    entry_point='gym_splendorm.envs:splendormEnv',
)