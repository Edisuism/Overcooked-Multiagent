import gym
from gym import spaces
import numpy as np
import random

class OvercookedEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, layout, start_positions, cook_time, max_steps):
        super(OvercookedEnv, self).__init__()
        self.layout = layout
        self.start_positions = start_positions
        self.cook_time = cook_time
        self.max_steps = max_steps
        self.players = [(0,0), (1,0)]
        self.ingredients = [(2,2), (2,3)]
        self.dishes = []
        self.steps = 0
        self.score = 0
        
        # Define action and observation spaces
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Dict({
            'players': spaces.Box(low=np.zeros((2, 2)), high=np.ones((2, 2)), dtype=np.float64),
            'ingredients': spaces.Box(low=np.zeros((2, 2)), high=np.ones((2, 2)), dtype=np.float64),
            'dishes': spaces.Box(low=np.zeros((2, 2)), high=np.ones((2, 2)), dtype=np.float64),
            'score': spaces.Box(low=-np.inf, high=np.inf, shape=(1,), dtype=np.float64),
        })

    def reset(self):
        self.players = self.start_positions
        self.ingredients = [(2,2), (2,3)]
        self.dishes = []
        self.steps = 0
        self.score = 0
        return self._get_obs()

    def step(self, action):
        self.steps += 1
        done = False
        
        # Move players
        self._move_player(0, action[0])
        self._move_player(1, action[1])
        
        # Serve dishes if both players are at the correct location
        if (len(self.dishes) == 2 and self.players[0] == self.dishes[0] and self.players[1] == self.dishes[1]):
            self.score += 10
            self.dishes = []
        
        # Cook dishes if there are enough ingredients
        for i in range(len(self.ingredients)):
            if (self.ingredients[i] == self.players[i]):
                self.ingredients[i] = None
                self.dishes.append(self.players[i])
                break
        
        # Penalize players for taking too long
        if (self.steps >= self.max_steps):
            self.score -= 1
            done = True
        
        # Update observation and score
        obs = self._get_obs()
        reward = self.score - obs['score']
        self.score = obs['score']
        
        return obs, reward, done, {}

    def render(self, mode='human'):
        for row in self.layout:
            for col in row:
                if (col == "#"):
                    print("#", end=" ")
                elif (col == "P1"):
                    print("P1", end=" ")
                elif (col == "P2"):
                    print("P2", end=" ")
                elif (col == "I"):
                    print("I", end=" ")
                elif (col == "D"):
                    print("D", end=" ")
                else:
                    print(" ", end=" ")
            print()
        print("Score: {}".format(self.score))
        
    def _move_player(self, player_num, direction):
        if (player_num < 1 or player_num > 2):
            raise ValueError("Invalid player number")
            # Determine new position
            new_pos = list(self.players[player_num-1])
            if (direction == 0):  # Up
                new_pos[0] -= 1
            elif (direction == 1):  # Down
                new_pos[0] += 1
            elif (direction == 2):  # Left
                new_pos[1] -= 1
            elif (direction == 3):  # Right
                new_pos[1] += 1
            else:
                raise ValueError("Invalid direction")
            
            # Check if new position is valid
            if (new_pos[0] < 0 or new_pos[0] >= len(self.layout) or new_pos[1] < 0 or new_pos[1] >= len(self.layout[0])):
                return
            if (self.layout[new_pos[0]][new_pos[1]] == "#"):
                return
            
            # Update position
            self.players[player_num-1] = tuple(new_pos)
    
    def _get_obs(self):
        obs = {
            'players': np.zeros(4),
            'ingredients': np.zeros((2,2)),
            'dishes': np.zeros((2,2)),
            'score': np.array([self.score]),
        }
        for i in range(2):
            obs['players'][i*2:(i+1)*2] = np.array(self.players[i])
            if (self.ingredients[i] is not None):
                obs['ingredients'][i] = np.array(self.ingredients[i])
            if (len(self.dishes) > i):
                obs['dishes'][i] = np.array(self.dishes[i])
        return obs
