import gym
from gym import spaces
from gym.utils import seeding
from gym.envs.registration import register
import numpy as np
import random

from settings import *
import pygame
import sys
import math
import copy
import csv
from os import path

register(id='Overcooked-v0', entry_point='overcookedenv:OvercookedEnv')


class OvercookedEnv(gym.Env):
    #metadata = {'render.modes' : ['human']}

    action_table = [[0,0,0,0,0], #NOTHING
                    [1,0,0,0,0], #UP
                    [0,1,0,0,0], #DOWN
                    [0,0,1,0,0], #LEFT
                    [0,0,0,1,0], #RIGHT
                    [0,0,0,0,1]] #INTERACT

    def __init__(self, *args):
        #print(args)
        self.game = GameSelfPlay('map.csv')
        self.policy = None
        self.action_space = spaces.Discrete(6)
        # self.observation_space = spaces.Box(low=0, high=51,
        #                                     shape=(5,6), dtype=np.int64)
        self.observation_space = self.game.generate_observation_space(self.game.state)

    def reset(self):
        obs = self.game.reset()
        return obs

    def step(self, action):
        obs, reward, done, info = self.game.step(action)
        return obs, reward, done, info

    def render(self, mode="human", close=False):
        self.game.draw()
    
    def _get_obs(self):
        obs = self.game.state
        return obs

class RandomPolicy:
    def __init__(self):
        pass

    def _getAction(self):
        action = random.randrange(0, 5)
        return action


class GameSelfPlay:
    def __init__(self, map_csv):
        pygame.init()
        pygame.display.set_caption(TITLE)
        pygame.key.set_repeat(500, 100)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 50)
        self.cook_font = pygame.font.SysFont(None, 25)
        self.visible_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.map = map_csv
        self.table = []
        self.grid = []
        self.grid_save = []
        self.agentOne = None
        self.agentTwo = None
        self.policy = RandomPolicy()
        self.pot = None
        self.counter = None
        self.food_dispenser = None
        self.plate_dispenser = None
        self.max_steps = 2500
        self.cooking_time = 50

        self.load_grid_from_csv(self.map)
        self.create_map()
        self.reset()
        

    def reset(self):
        self.grid = copy.deepcopy(self.grid_save)
        self.agentOne.reset()
        self.agentTwo.reset()

        #randomly switch agent positions
        random_number = random.randint(0, 1)
        if random_number == 1:
            tempX = self.agentOne.x
            tempY = self.agentOne.y
            self.agentOne.x = self.agentTwo.x
            self.agentOne.y = self.agentTwo.y
            self.agentTwo.x = tempX
            self.agentTwo.y = tempY

        for table in self.table:
            table.reset()
        self.pot.reset()

        self.playing = True
        self.is_cooking = False
        self.score = 0
        self.cook_counter = 0
        self.gameover = False
        self.current_step = 0
        self.initialise_dictionary_state()

        return self.state


    def step(self, action):
        self.draw()
        self.update_grid()
        self.agentOne.setAction(action)
        self.agentTwo.setAction(self.policy._getAction())
        self.agentOne.update()
        self.agentTwo.update()
        self.pot.update()

        self.current_step += 1

        if (self.is_cooking):
            self.cook_counter += 1
            if (self.cook_counter >= self.cooking_time):
                self.pot.finish_cook()
                self.cook_counter = 0

        if (self.current_step >= self.max_steps):
            self.agentOne.add_score(self.score)
            self.agentTwo.add_score(self.score)
            self.gameover = True

        agentTwoReward = self.agentTwo.temp_score()
        reward = self.agentOne.temp_score()

        self.update_score()
        self.update_time()

        observation = self.state

        done = self.gameover

        info = {"agentOne_archetype": self.agentOne.archetype.get_archetype(),
                "agentTwo_archetype": self.agentTwo.archetype.get_archetype()
        }

        #self.write_to_csv()

        return observation, reward, done, info

    def handle_player_events(self):
        action = self.events()
        self.step(action)

    def events(self):
        action = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_r:
                    self.reset()
            
            if self.gameover:
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    action = 3
                elif event.key == pygame.K_RIGHT:
                    action = 4
                elif event.key == pygame.K_UP:
                    action = 2
                elif event.key == pygame.K_DOWN:
                    action = 1
                elif event.key == pygame.K_RCTRL:
                    action = 5

        return action

    def load_grid_from_csv(self, FILENAME):
        game_folder = path.dirname(__file__)
        with open(path.join(game_folder, FILENAME), 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                row = [int(value) for value in line]
                self.grid.append(row) 
        self.grid_save = copy.deepcopy(self.grid)

# self.num_of_objects_placed = 0
# self.num_of_objects_boiled = 0
# self.num_of_soup_delivered = 0
# self.num_of_soup_plated = 0
# self.distance_moved = 0
    def write_to_csv(self):
        with open('archetype.csv', mode='a', newline='') as file:
            writer = csv.writer(file)

            randomNumber = random.randint(1, 20)

            if randomNumber < 3:
                writer.writerow([random.randint(13, 20),random.randint(1, 5),random.randint(0, 1),random.randint(0, 1),random.randint(50, 80)])
            elif randomNumber < 10:
                writer.writerow([random.randint(1, 2),random.randint(8, 14),random.randint(0, 3),random.randint(0, 3),random.randint(50, 80)])
            elif randomNumber < 16:
                writer.writerow([random.randint(0, 2),random.randint(10, 19),random.randint(0, 3),random.randint(0, 3),random.randint(50, 100)])
            elif randomNumber < 21:
                writer.writerow([random.randint(5, 10),random.randint(5, 10),random.randint(0, 2),random.randint(0, 2),random.randint(100, 200)])
            #writer.writerow(info["agentOne_archetype"])
            #writer.writerow(info["agentTwo_archetype"])

    def create_map(self):
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                if tile == 0:
                    pass
                elif tile == 10:
                    self.table.append(Table(self, col_index, row_index))
                elif tile == 30:
                    self.plate_dispenser = PlateDispenser(self, col_index, row_index)
                elif tile == 20:
                    self.pot = Pot(self, col_index, row_index)
                elif tile == 40:
                    self.counter = Counter(self, col_index, row_index)
                elif tile == 50:
                    self.food_dispenser = FoodDispenser(self, col_index, row_index)
                elif tile == 1:
                    self.agentOne = Player(self, col_index, row_index, 1)
                    self.agentOne.name = "1"
                elif tile == 5:
                    self.agentTwo = Player(self, col_index, row_index, 5)
                    self.agentTwo.name = "2"

    
    def update(self):
        self.visible_sprites.update()

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.visible_sprites.draw(self.screen)
        self.draw_UI()
        pygame.display.flip()

    def update_grid(self):
        #invert x and y to fit with gridworld
        #shouldn't need to do an if check for moving into another agents past tile as players are obstacles
        self.grid[self.agentOne.past_y][self.agentOne.past_x] = 0
        self.grid[self.agentOne.y][self.agentOne.x] = self.agentOne.current_id

        self.grid[self.agentTwo.past_y][self.agentTwo.past_x] = 0
        self.grid[self.agentTwo.y][self.agentTwo.x] = self.agentTwo.current_id

        for table in self.table:
            self.grid[table.y][table.x] = table.id
        
        self.pot.update()
        self.grid[self.pot.y][self.pot.x] = self.pot.id

    def draw_UI(self):
        # score
        self.text = self.font.render("Score: " + str(self.score), True, (255, 0, 0))
        text_rect = self.text.get_rect(topright = self.screen.get_rect().topright)
        self.screen.blit(self.text, text_rect)

        if self.max_steps - self.current_step > 0:
            self.text = self.font.render("Time: " + str(self.max_steps - self.current_step ), True, (255, 0, 0))
            text_rect = self.text.get_rect(topleft = self.screen.get_rect().topleft)
            self.screen.blit(self.text, text_rect)
        if self.max_steps - self.current_step <= 0:
            self.text = self.font.render("Game Finished!", True, (255, 0, 0))
            text_rect = self.text.get_rect(topleft = self.screen.get_rect().topleft)
            self.screen.blit(self.text, text_rect)
            self.gameover = True

    def get_game_state(self):
        return self.grid

 # Dictionary logic start
    def initialise_dictionary_state(self):
        self.state = {
            "agent_position_1": np.array([self.agentOne.y, self.agentOne.x], dtype=np.int8),
            "agent_orientation_1": np.array([int(self.agentOne.orientation)], dtype=np.int8),
            "agent_has_object_1": np.array(self.agentOne.get_held(), dtype=np.int8),
            "agent_position_2": np.array([self.agentTwo.y, self.agentTwo.x], dtype=np.int8),
            "agent_orientation_2": np.array([int(self.agentTwo.orientation)], dtype=np.int8),
            "agent_has_object_2": np.array(self.agentTwo.get_held(), dtype=np.int8),
            "food_dispenser_position": np.array([self.food_dispenser.y, self.food_dispenser.x], dtype=np.int8),
            "plate_dispenser_position": np.array([self.plate_dispenser.y, self.plate_dispenser.x], dtype=np.int8),
            "pot_0_position": np.array([self.pot.y, self.pot.x], dtype=np.int8),
            "pot_0_num_objects": np.array([len(self.pot.objects)], dtype=np.int8),
            "counter_0_position": np.array([self.counter.y, self.counter.x], dtype=np.int8),
            "score": np.array([self.score], dtype=np.int8),
            "time": np.array([self.max_steps - self.current_step], dtype=np.int8),
        }

        for i in range (len(self.table)):
            self.state[f"table_{i}_position"] = np.array([self.table[i].y, self.table[i].x], dtype=np.int8)
            self.state[f"object_position_{i}"] = np.array([np.finfo(np.float32).max, np.finfo(np.float32).max ], dtype=np.float32)
            self.state[f"object_type_{i}"] = np.array([0, 0, 0], dtype=np.int8)

    def generate_observation_space(self, state):
        observation = spaces.Dict({
            "agent_position_1": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "agent_orientation_1": spaces.Box(low=0, high=8, shape=(1,), dtype=np.int8),
            "agent_has_object_1": spaces.Box(low=0, high=1, shape=(3,), dtype=np.int8),
            "agent_position_2": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "agent_orientation_2": spaces.Box(low=0, high=8, shape=(1,), dtype=np.int8),
            "agent_has_object_2": spaces.Box(low=0, high=1, shape=(3,), dtype=np.int8),
            "food_dispenser_position": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "plate_dispenser_position": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "pot_0_position": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "pot_0_num_objects": spaces.Box(low=0, high=3, shape=(1,), dtype=np.int8),
            "counter_0_position": spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8),
            "score": spaces.Box(low=0, high=np.finfo(np.float32).max, shape=(1,), dtype=np.float32),
            "time": spaces.Box(low=-np.finfo(np.float32).max, high=np.finfo(np.float32).max, shape=(1,), dtype=np.float32),
        })

        table_space = spaces.Box(low=0, high=6, shape=(2,), dtype=np.int8)
        object_position_space = spaces.Box(low=0, high=np.finfo(np.float32).max, shape=(2,), dtype=np.float32)
        object_type_space = spaces.Box(low=0, high=1, shape=(3,), dtype=np.int8)

        for i in range (len(self.table)):
            observation[f"table_{i}_position"] = table_space

        for i in range (len(self.table)):       
            observation[f"object_position_{i}"] = object_position_space
            observation[f"object_type_{i}"] = object_type_space

        return observation


    def flatten_dictionary(self):
        obs = np.concatenate([self.state[k].flatten() for k in sorted(self.state.keys())])
        return obs
    
    def get_next_object(self):
        for key in self.state.keys():
            if key.startswith("object_type") and np.array_equal(self.state[key], np.array([0, 0, 0], dtype=np.int8)):
                return key[-1]
        return None

    def update_object(self, obj_name, x, y, obj_type):
        self.state[f"object_type_{obj_name}"] = np.array(obj_type, dtype=np.int8)
        self.state[f"object_position_{obj_name}"] = np.array([y, x], dtype=np.float32)

    def delete_object(self, obj_name):
        del self.state[obj_name]

    def update_agent(self, geom_name, x, y, orientation, has_object):
        self.state[f"agent_position_{geom_name}"] = np.array([y,x], dtype=np.int8)
        self.state[f"agent_orientation_{geom_name}"] = np.array([orientation], dtype=np.int8)
        self.state[f"agent_has_object_{geom_name}"] = np.array(has_object, dtype=np.int8)

    def update_pot(self, x, y, num_objects):
        self.state["pot_0_position"] = np.array([y,x], dtype=np.int8)
        self.state["pot_0_num_objects"] = np.array([num_objects], dtype=np.int8)

    def update_score(self):
        self.state["score"] = np.array([self.score], dtype=np.float32)

    def update_time(self):
        self.state["time"] = np.array([self.max_steps - self.current_step], dtype=np.float32)
 # Dictionary logic end

    def visualise_grid(self , grid):
        print("{:<5}".format(""), end="|")
        for col in range(len(grid[0])):
            print("{:^5}".format(f"Col {col}"), end="|")
        print("\n" + "-"*len("{:<5}".format("")) + "-"*(6*len(grid[0])+1))
        for row in range(len(grid)):
            print("{:<5}".format(f"Row {row}"), end="|")
            for col in range(len(grid[row])):
                print("{:^5}".format(str(grid[row][col])), end="|")
            print("\n" + "-"*len("{:<5}".format("")) + "-"*(6*len(grid[row])+1))

    def getDistance(grid, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def add_score(amount):
        self.score += amount



class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y, _id):
        groups = game.visible_sprites, game.obstacles
        super().__init__(groups)
        self.game = game
        self.sprites = [pygame.image.load(os.path.dirname(__file__) + f"/Sprites/chef_{name}.png").convert_alpha()
                        for name in ["front", "back", "side", "front_plate", "side_plate", "front_food", "side_food", "front_soup", "side_soup"]]
        self.image = self.sprites[0] 
        self.rect = self.image.get_rect()
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.desired_x = 0
        self.desired_y = 0
        self.past_x = x
        self.past_y = y
        self.interacting = False 
        self.still = False
        self.orientation = 6
        self.score = 0
        self.tempScore = 0
        self.held = None
        self.original_id = _id
        self.current_id = _id
        self.identity = None
        self.set_identity()
        self.name = None
        self.archetype = Archetype()
        self.action_table = [[0,0,0,0,0], #NOTHING
                            [1,0,0,0,0], #UP
                            [0,1,0,0,0], #DOWN
                            [0,0,1,0,0], #LEFT
                            [0,0,0,1,0], #RIGHT
                            [0,0,0,0,1]] #INTERACT


    def discreteActions(self, n):
        return self.action_table[n]

    def setAction(self, action):
        self.interacting = False
        self.still = False

        action = self.discreteActions(action)

        if action[0] > 0:
            self.desired_y = 1
        elif action[1] > 0:
            self.desired_y = -1
        elif action[2] > 0:
            self.desired_x = -1
        elif action[3] > 0:
            self.desired_x = 1
        elif action[4] > 0:
            self.interacting = True
        else:
            self.still = True
    
    def move(self, dx=0, dy=0):
        orientation_map = {(1, 0): 6, (-1, 0): 4, (0, 1): 2, (0, -1): 8}
        if (dx, dy) in orientation_map:
            self.orientation = orientation_map[(dx, dy)]
        if not self.collide_with_obstacles(dx, dy):
            self.past_x = self.x
            self.past_y = self.y
            self.x += dx
            self.y += dy
            self.archetype.distance_moved += 1

    def collide_with_obstacles(self, dx=0, dy=0):
         return any(obstacle.x == self.x + dx and obstacle.y == self.y + dy for obstacle in self.game.obstacles)

    def interact(self):
        dx, dy = {6: (1, 0), 4: (-1, 0), 2: (0, 1), 8: (0, -1)}[self.orientation]
        self.use_interactable(dx, dy)

    def use_interactable(self, dx=0, dy=0):
        for interactable in self.game.interactables:
            if interactable.x == self.x + dx and interactable.y == self.y + dy:
                interactable.invoke(self)

    def update(self):
        if (self.interacting):
            self.interact()
        self.move(self.desired_x, self.desired_y)
        self.clear_action()

        # Update ID
        if isinstance(self.held, Food):
            self.current_id = self.original_id + 1
        if isinstance(self.held, Plate):
            self.current_id = self.original_id + 2
        if isinstance(self.held, Soup):
            self.current_id = self.original_id + 3

        # attempt to incentivise player to deliver soup
        if (isinstance(self.held, Soup)):
            distance = self.game.getDistance(self.x, self.y, self.game.counter.x, self.game.counter.y)
            if distance < 3:
                self.add_score(4 - distance)

        has_object = 0
        if (self.held != None):
            has_object = 1
            #self.game.update_object(self.held.obj_name, self.x, self.y, 0)
            self.held.remove_from_dictionary()

        self.game.update_agent(self.name, self.x, self.y, self.orientation, self.get_held())
        self.render()

    def clear_action(self):
        self.desired_x = 0
        self.desired_y = 0
        self.interacting = False

    def render(self):
        self.rect.x = self.x * TILESIZE
        self.rect.y = self.y * TILESIZE
        if self.orientation == 6:
            self.image = pygame.transform.flip(self.sprites[2], True, False)
            if isinstance(self.held, Plate):
                self.image = pygame.transform.flip(self.sprites[4], True, False)
            if isinstance(self.held, Food):
                self.image = pygame.transform.flip(self.sprites[6], True, False)
            if isinstance(self.held, Soup):
                self.image = pygame.transform.flip(self.sprites[8], True, False)
        if self.orientation == 4: 
            self.image = self.sprites[2]
            if isinstance(self.held, Plate):
                    self.image = self.sprites[4]       
            if isinstance(self.held, Food):
                    self.image = self.sprites[6]  
            if isinstance(self.held, Soup):
                self.image = self.sprites[8]  
        if self.orientation == 2: 
            self.image = self.sprites[0]
            if isinstance(self.held, Plate):
                self.image = self.sprites[3]  
            if isinstance(self.held, Food):
                self.image = self.sprites[5]
            if isinstance(self.held, Soup):
                self.image = self.sprites[7]
        if self.orientation == 8: 
            self.image = self.sprites[1]  

    # return the score gained the current frame, if score is 0 then return -1
    def temp_score(self):
        scoreContainer = self.tempScore
        scoreContainer -= 1
        self.tempScore = 0
        return scoreContainer
        

    def add_score(self, amount):
        self.score += amount
        #self.game.score += amount
        self.tempScore += amount

    def get_position(self):
        return (self.x, self.y)

    def set_identity(self):
        self.identity = id(self)

    def get_identity(self):
        return self.identity

    def get_held(self):
        if self.held == None:
            return [0,0,0]
        elif isinstance(self.held, Food):
            return [1,0,0]
        elif isinstance(self.held, Plate):
            return [0,1,0]
        elif isinstance(self.held, Soup):
            return [0,0,1]

    def reset(self):
        self.image = self.sprites[0] 
        self.x = self.original_x
        self.y = self.original_y
        self.desired_x = 0
        self.desired_y = 0
        self.past_x = self.x
        self.past_y = self.y
        self.interacting = False 
        self.still = False
        self.orientation = 6
        self.score = 0
        if self.held:
            del self.held
        self.held = None
        self.identity = None
        self.set_identity()

class Archetype():
    def __init__(self): 
        self.num_of_objects_placed = 0
        self.num_of_objects_boiled = 0
        self.num_of_soup_delivered = 0
        self.num_of_soup_plated = 0
        self.distance_moved = 0

    def get_archetype(self):
        return [self.num_of_objects_placed, self.num_of_objects_boiled, self.num_of_soup_delivered, self.num_of_soup_plated, self.distance_moved]

    @property
    def num_of_objects_placed(self):
        return self._num_of_objects_placed

    @num_of_objects_placed.setter
    def num_of_objects_placed(self, value):
        self._num_of_objects_placed = value

    @property
    def num_of_objects_boiled(self):
        return self._num_of_objects_boiled

    @num_of_objects_boiled.setter
    def num_of_objects_boiled(self, value):
        self._num_of_objects_boiled = value

    @property
    def num_of_soup_delivered(self):
        return self._num_of_soup_delivered

    @num_of_soup_delivered.setter
    def num_of_soup_delivered(self, value):
        self._num_of_soup_delivered = value

    @property
    def num_of_soup_plated(self):
        return self._num_of_soup_plated

    @num_of_soup_plated.setter
    def num_of_soup_plated(self, value):
        self._num_of_soup_plated = value

    @property
    def distance_moved(self):
        return self._distance_moved

    @distance_moved.setter
    def distance_moved(self, value):
        self._distance_moved = value


# Tile classes
class Interactable(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.visible_sprites, game.obstacles, game.interactables
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game, self.x, self.y = game, x, y
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x * TILESIZE, y * TILESIZE

    def invoke(self):
        pass

    def get_position(self):
        return (self.x, self.y)


class Table(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = TILE
        self.object = None
        self.id = 10

    def invoke(self, player):
        if self.object:
            if player.held == None:
                player.held = self.object
                player.held.remove_from_dictionary()
                self.object = None
                self.image = TILE
        else:
            if (player.held):
                self.object = player.held
                player.held.player = self
                self.object.initialise_in_dictionary()
                player.held = None
                player.archetype.num_of_objects_placed += 1
                if isinstance(self.object, Food):
                    self.image = TILE_FOOD
                    self.id = 11
                if isinstance(self.object, Plate):
                    self.image = TILE_PLATE
                    self.id = 12
                if isinstance(self.object, Soup):
                    self.image = TILE_SOUP
                    self.id = 13
    
    def reset(self):
        if self.object:
            del self.object
        self.object = None
        self.image = TILE
        self.id = 10


class FoodDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = DISPENSER

    def invoke(self, player):
        if player.held == None:
            player.held = Food(self.game, player)
        elif isinstance(player.held, Food):
            player.held.remove_from_dictionary()
            player.held = None
                
class PlateDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = PLATE_DISPENSER

    def invoke(self, player):
        if player.held == None:
            player.held = Plate(self.game, player)
        elif isinstance(player.held, Plate):
            player.held.remove_from_dictionary()
            player.held = None

class Pot(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = POT
        self.id = 20
        self.objects = []
        self.time_to_cook = 3
        self.is_cooked = False
    
    def invoke(self, player):
        if (len(self.objects) < 3 and isinstance(player.held, Food)):
            self.objects.append(player.held)
            player.held.remove_from_dictionary()
            player.held = None
            player.add_score(1) 
            player.archetype.num_of_objects_boiled += 1
            if (len(self.objects) == 3):
                self.is_cooked = True
        if (self.is_cooked):
            if isinstance(player.held, Plate):
                self.is_cooked = False
                object_id_list = []
                object_id_list.append(player.held.get_owner())
                for ingredient in self.objects:
                    object_id_list.append(ingredient.get_owner())

                player.held = Soup(self.game, player, object_id_list)
                player.add_score(1) 
                player.archetype.num_of_soup_plated += 1
                self.objects.clear()

    def cook(self):
        self.game.is_cooking = True

    def finish_cook(self):
        self.is_cooked = True
        self.game.is_cooking = False
    
    def update(self):
        self.image = [POT, POT_1, POT_2, POT_3, POT_DONE][len(self.objects) + self.is_cooked]
        self.id = len(self.objects) + self.is_cooked + 20
        self.game.update_pot(self.x, self.y, len(self.objects))
 
    def reset(self):
        self.image = POT
        self.id = 20
        for ingredient in self.objects:
            del ingredient
        self.objects.clear()
        self.is_cooked = False

class Counter(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image.fill(LIGHTGREY)
        self.x = x
        self.y = y

    def invoke(self, player):
        if isinstance(player.held, Soup):
            self.game.score += 100
            player.add_score(40) 
            # Reward use of ingredients and plate
            for identity in player.held.get_ingredients():
                identity.add_score(20)

            player.held.remove_from_dictionary()
            player.held = None
            player.archetype.num_of_soup_delivered += 1
            print(self.game.agentOne.score)
            print(self.game.agentTwo.score)

class Plate:
    def __init__(self, game, player):
        self.player = player
        self.player.held = self
        self.full = False
        self.owner = player
        self.game = game
        self.obj_name = None
    
    def get_owner(self):
        return self.owner

    def get_pos(self):
        return self.player.x, self.player.y

    def initialise_in_dictionary(self):
        self.obj_name = self.game.get_next_object()
        self.game.update_object(self.obj_name, self.player.x, self.player.y, [0,1,0])

    def remove_from_dictionary(self):
        self.game.update_object(self.obj_name, np.finfo(np.float32).max, np.finfo(np.float32).max, [0,0,0])
        self.obj_name = None

class Food:
    def __init__(self, game, player):
        self.player = player
        self.player.held = self
        self.owner = player
        self.game = game
        self.obj_name = None

    def get_owner(self):
        return self.owner

    def get_pos(self):
        return self.player.x, self.player.y
    
    def initialise_in_dictionary(self):
        self.obj_name = self.game.get_next_object()
        self.game.update_object(self.obj_name, self.player.x, self.player.y, [1,0,0])

    def remove_from_dictionary(self):
        self.game.update_object(self.obj_name, np.finfo(np.float32).max, np.finfo(np.float32).max, [0,0,0])
        self.obj_name = None


class Soup:
    def __init__(self, game, player, ingredients):
        self.player = player
        self.player.held = self
        self.ingredients = ingredients
        self.owner = player
        self.game = game
        self.obj_name = None

    def get_owner(self):
        return self.owner

    def get_ingredients(self):
        return self.ingredients

    def get_pos(self):
        return self.player.x, self.player.y

    def initialise_in_dictionary(self):
        self.obj_name = self.game.get_next_object()
        self.game.update_object(self.obj_name, self.player.x, self.player.y, [0,0,1])

    def remove_from_dictionary(self):
        self.game.update_object(self.obj_name, np.finfo(np.float32).max, np.finfo(np.float32).max, [0,0,0])
        self.obj_name = None

if __name__ == "__main__":
    game = GameSelfPlay('map.csv')
    game.initialise_dictionary_state()
    while True:
        game.handle_player_events()
