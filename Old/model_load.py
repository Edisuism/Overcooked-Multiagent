import gym
from os import path
from stable_baselines3 import PPO


#from overcookedenv import OvercookedSelfPlayEnv


# env = OvercookedSelfPlayEnv
# env.reset()

# models_dir = "ppo2_selfplay"
# model_path = f"{models_dir}/best_model.zip"

# model = PPO.load(model_path, env=env)

# episodes = 10

# for ep in range (episodes):
#     obs = env.reset()
#     done = False
#     while not done:
#         env.render()
#         action, _ = model.predict(obs)
#         obs, reward, done, info = env.step(action)

# env.close()