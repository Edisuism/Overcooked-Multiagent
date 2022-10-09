from overcookedenv import OvercookedEnv

env = OvercookedEnv()
episodes = 1

for episode in range(episodes):
    done = False
    obs = env.reset()
    while True:
        random_action = env.action_space.sample()
        random_other_action = env.action_space.sample()
        print("action", random_action)
        obs, reward, done, info  = env.step(random_action, random_other_action)
        print("reward", reward)
        done = env.done