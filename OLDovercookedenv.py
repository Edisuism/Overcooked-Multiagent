import gym
import pygame
import main
from gym import spaces
import sys
from settings import *
from sprites_r import *
import os
from os import path
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import EvalCallback

from shutil import copyfile # keep track of generations

# Settings
NUM_TIMESTEPS = int(1e9)
EVAL_FREQ = int(1e5)
EVAL_EPISODES = int(1e2)
BEST_THRESHOLD = 0.5 # must achieve a mean score above this to replace prev best self

RENDER_MODE = False # set this to false if you plan on running for full 1000 trials.

LOGDIR = "ppo2_selfplay"



class OvercookedEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    super(OvercookedEnv, self).__init__()
    self.game = main.Game()
    self.game.create_map()
    self.action_space = spaces.Discrete(6)
    self.observation_space = spaces.Box(low=-500.0, high=500.0, shape=(8,), dtype=np.int64)
    self.agent = self.game.player[0]
    self.agentOther = self.game.player[1]
    #self.policy = BaselinePolicy()
    

  def step(self, action, otheraction=None):
    self.done = self.game.gameover
    self.game.events()
    self.game.update()
    self.game.draw()
    self.observation = [self.game.player[0].x, self.game.player[0].y, self.game.player[1].x, self.game.player[1].y, self.game.pot.x, self.game.pot.y, 
                        self.game.counter.x, self.game.counter.y]
    self.observation = np.array(self.observation)

    if otheraction is None:
      otheraction = self.action_space.sample()
      #otheraction = self.otherAction
    # if self.otherAction is not None:
    #   otherAction = self.otherAction
      
    # if otherAction is None: # override baseline policy
    #   obs = self.game.player[0].getObservation()
    #   otherAction = self.policy.predict(obs)

    # self.game.player[0].setAction(otherAction)
    # self.game.player[1].setAction(action) 

    # action 0 is doing nothing 
    if action == 1:
        self.game.player[0].move(dx=-1)
    if action == 2:
        self.game.player[0].move(dx=1)
    if action == 3:
        self.game.player[0].move(dy=-1)
    if action == 4:
        self.game.player[0].move(dy=1)
    if action == 5:
        self.game.player[0].interact()
    # action 0 is doing nothing 
    if otheraction == 1:
        self.game.player[1].move(dx=-1)
    if otheraction == 2:
        self.game.player[1].move(dx=1)
    if otheraction == 3:
        self.game.player[1].move(dy=-1)
    if otheraction == 4:
        self.game.player[1].move(dy=1)
    if otheraction == 5:
        self.game.player[1].interact()
      

    self.reward = self.game.score
    if (self.game.is_cooking):
      self.reward += 0.001

    info = {}
    return self.observation, self.reward, self.done, info


  def reset(self):
    self.game.restart()
    self.observation= [self.game.player[0].x, self.game.player[0].y, self.game.player[1].x, self.game.player[1].y, self.game.pot.x, self.game.pot.y,    
                       self.game.counter.x, self.game.counter.y]
    self.observation = np.array(self.observation)
    return self.observation  # reward, done, info can't be included


#   def render(self, mode='human'):
#     ...
#   def close (self):
#     ...


class OvercookedSelfPlayEnv(OvercookedEnv):
 # wrapper over the normal single player env, but loads the best self play model
  def __init__(self):
    super(OvercookedSelfPlayEnv, self).__init__()
    self.policy = self
    self.best_model = None
    self.best_model_filename = None
  def predict(self, obs): # the policy
    if self.best_model is None:
      return self.action_space.sample() # return a random action
    else:
      action, _ = self.best_model.predict(obs)
      return action
  def reset(self):
    # load model if it's there
    modellist = [f for f in os.listdir(LOGDIR) if f.startswith("history")]
    modellist.sort()
    if len(modellist) > 0:
      filename = os.path.join(LOGDIR, modellist[-1]) # the latest best model
      if filename != self.best_model_filename:
        print("loading model: ", filename)
        self.best_model_filename = filename
        if self.best_model is not None:
          del self.best_model
        self.best_model = PPO.load(filename, env=self)
    return super(OvercookedSelfPlayEnv, self).reset()

class SelfPlayCallback(EvalCallback):
  # hacked it to only save new version of best model if beats prev self by BEST_THRESHOLD score
  # after saving model, resets the best score to be BEST_THRESHOLD
    def __init__(self, *args, **kwargs):
        super(SelfPlayCallback, self).__init__(*args, **kwargs)
        self.best_mean_reward = BEST_THRESHOLD
        self.generation = 0

    def _on_step(self) -> bool:
        result = super(SelfPlayCallback, self)._on_step()
        if result and self.best_mean_reward > BEST_THRESHOLD:
            self.generation += 1
            print("SELFPLAY: mean_reward achieved:", self.best_mean_reward)
            print("SELFPLAY: new best model, bumping up generation to", self.generation)
            source_file = os.path.join(LOGDIR, "best_model.zip")
            backup_file = os.path.join(LOGDIR, "history_"+str(self.generation).zfill(8)+".zip")
            copyfile(source_file, backup_file)
            self.best_mean_reward = BEST_THRESHOLD
        return result
    
def rollout(env, policy):
    """ play one agent vs the other in modified gym-style loop. """
    obs = env.reset()

    done = False
    total_reward = 0

    while not done:

        action, _states = policy.predict(obs)
        obs, reward, done, _ = env.step(action)

        total_reward += reward

        if RENDER_MODE:
            env.render()

    return total_reward

def train():
    # train selfplay agent
    customlogger = configure(folder=LOGDIR)

    env = OvercookedSelfPlayEnv()

    # take mujoco hyperparams (but doubled timesteps_per_actorbatch to cover more steps.)
    model = PPO("MlpPolicy", env, n_steps=4096, clip_range=0.2, ent_coef=0.0, n_epochs=10,
                    batch_size=64, gamma=0.99, gae_lambda=0.95, verbose=2)
    
    model.set_logger(customlogger)

    eval_callback = SelfPlayCallback(env,
        best_model_save_path=LOGDIR,
        log_path=LOGDIR,
        eval_freq=EVAL_FREQ,
        n_eval_episodes=EVAL_EPISODES,
        deterministic=False)

    model.learn(total_timesteps=NUM_TIMESTEPS, callback=eval_callback)

    model.save(os.path.join(LOGDIR, "final_model")) # probably never get to this point.

    env.close()


train()

