import gym
from overcookedenv import OvercookedEnv

# Register the environment
gym.envs.register(
    id='OvercookedAI-v0',
    entry_point='overcookedenv:OvercookedEnv'
)

# Create an instance of the environment
env = gym.make('OvercookedAI-v0', layout=["#  #", "#  #", "## ##"], start_positions=[(0,0), (2,4)], cook_time = 3, max_steps = 10000)
print(env.layout)