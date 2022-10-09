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




class OvercookedEnv(gym.Env):
  metadata = {'render.modes': ['human']}

  def __init__(self):
    super(OvercookedEnv, self).__init__()
    self.game = main.Game()
    self.game.create_map()
    self.action_space = spaces.Discrete(6)
    self.observation_space = spaces.Box(low=-500.0, high=500.0, shape=(4,), dtype=np.int64)
    

  def step(self, action, otheraction):
    self.done = self.game.gameover
    self.game.events()
    self.game.update()
    self.game.draw()
    self.observation = [self.game.player[0].x, self.game.player[0].y, self.game.player[1].x, self.game.player[1].y]
    self.observation = np.array(self.observation)

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
    info = {}
    return self.observation, self.reward, self.done, info


  def reset(self):
    self.game.restart()
    self.observation= [self.game.player[0].x, self.game.player[0].y, self.game.player[1].x, self.game.player[1].y]
    self.observation = np.array(self.observation)
    return self.observation  # reward, done, info can't be included


#   def render(self, mode='human'):
#     ...
#   def close (self):
#     ...