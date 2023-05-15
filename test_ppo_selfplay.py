import os
import numpy as np
import gym
import overcookedenv

from stable_baselines3 import PPO
from stable_baselines3.ppo import MlpPolicy
from stable_baselines3.ppo import MultiInputPolicy
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor

# load a pre-trained model
model = PPO.load("my_model")

# create a Gym environment to test the model on
env = gym.make("Overcooked-v0")

# run the model in the environment for a few episodes
for i in range(5):
    obs = env.reset()
    done = False
    total_reward = 0
    while not done:
        action, _ = model.predict(obs)
        obs, reward, done, _ = env.step(action)
        total_reward += reward
    print(f"Episode {i}: Total reward = {total_reward}")