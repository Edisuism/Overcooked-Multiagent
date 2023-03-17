import gym
from gym import spaces
import numpy as np
import random

from settings import *
import pygame
import sys
import math
import copy
import csv
from os import path

class OvercookedEnv(gym.Env):
    #metadata = {'render.modes' : ['human']}
    def __init__(self):
        self.pygame = PyGame2D()
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(np.array([0, 0, 0, 0, 0]), np.array([10, 10, 10, 10, 10]), dtype=np.int)

    def reset(self):
        del self.pygame
        self.pygame = PyGame2D()
        obs = self.pygame.observe()
        return obs

    def step(self, action):
        self.pygame.action(action)
        obs = self.pygame.observe()
        reward = self.pygame.evaluate()
        done = self.pygame.is_done()
        return obs, reward, done, {}

    def render(self, mode="human", close=False):
        self.pygame.view()
    
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


class GameSelfPlay:
    # ___Init___

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
        self.pot = None
        self.counter = None
        self.food_dispenser = None
        self.plate_dispenser = None

        self.load_grid_from_csv(self.map)
        self.create_map()
        self.reset()



    def handle_player_events(self):
        while self.playing:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()
            while current_time > TIME_STEP:
                self.events()
                self.ai_update()

                if (self.is_cooking):
                    self.cook_counter += 1
                    if (self.cook_counter >= cooking_time):
                        self.pot.finish_cook()
                        self.cook_counter = 0

                self.update_grid()
                self.update()
                self.draw()
                current_time -= TIME_STEP


    def events(self):
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

                #if event.type == TIMER_EVENT:
                    #self.ai_update()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.agentOne.setAction([0,0,1,0,0])
                    if event.key == pygame.K_RIGHT:
                        self.agentOne.setAction([0,0,0,1,0])
                    if event.key == pygame.K_UP:
                        self.agentOne.setAction([0,1,0,0,0])
                    if event.key == pygame.K_DOWN:
                        self.agentOne.setAction([1,0,0,0,0])
                    if event.key == pygame.K_RCTRL:
                        self.agentOne.setAction([0,0,0,0,1])
                    self.update_grid()


    def reset(self):
        # self.visible_sprites.empty()
        # self.obstacles.empty()
        # self.interactables.empty()
        self.grid = copy.deepcopy(self.grid_save)
        self.agentOne.reset()
        self.agentTwo.reset()
        for table in self.table:
            table.reset()
        self.pot.reset()

        self.playing = True
        self.is_cooking = False
        self.score = 0
        self.game_length = 20
        self.cook_time = 3
        self.cook_counter = 3
        self.start_counter = 0
        self.gameover = False
        self.visualise_grid(self.grid)


    def step(self, action):
        self.agentOne.update()
        self.agentTwo.update()

        self.cook_counter -= 1
        if (cook_counter <= 0):
            self.pot.finish_cook()
            self.cook_counter = self.cook_time

    def load_grid_from_csv(self, FILENAME):
        game_folder = path.dirname(__file__)
        with open(path.join(game_folder, FILENAME), 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                row = [int(value) for value in line]
                self.grid.append(row) 
        self.grid_save = copy.deepcopy(self.grid)

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
                    self.agentOne = Player(self, col_index, row_index)
                elif tile == 2:
                    self.agentTwo = Player(self, col_index, row_index)

    
    def update(self):
        self.visible_sprites.update()

    def ai_update(self):
        action = [0,0,0,0,0]
        index = random.randint(0,4)
        #action[index] = random.randint(0,1)
        action[index] = 1
        self.agentTwo.setAction(action)

    def draw(self):
        self.screen.fill(BGCOLOR)
        #self.draw_grid()
        self.visible_sprites.draw(self.screen)
        #self.draw_UI()
        pygame.display.flip()

    def update_grid(self):
        #invert x and y to fit with gridworld
        self.grid[self.agentOne.past_y][self.agentOne.past_x] = 0
        self.grid[self.agentOne.y][self.agentOne.x] = 1

        self.grid[self.agentTwo.past_y][self.agentTwo.past_x] = 0
        self.grid[self.agentTwo.y][self.agentTwo.x] = 2

        for table in self.table:
            self.grid[table.y][table.x] = table.id
        
        self.pot.update()
        self.grid[self.pot.y][self.pot.x] = self.pot.id

    def get_game_state(self):
        return self.grid

    def get_mini_state(self):
        state = {
            "agentOne_x": self.agentOne.x,
            "agentOne_y": self.agentOne.y,
            "agentTwo_x": self.agentTwo.x,
            "agentTwo_y": self.agentTwo.y,
            "pot_x": self.pot.x,
            "pot_y": self.pot.y,
            "pot_count": len(self.pot.objects),
            "counter_x": self.counter.x,
            "counter_y": self.counter.y,   
            "items":
            {
                "onion1_x": self.food_dispenser.x,
                "onion1_y": self.food_dispenser.y,
                "plate1_x": self.plate_dispenser.x,
                "plate1_y": self.plate_dispenser.y,
            }
        }
        return state


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

#Action_table = [0,0,0,0,0] nothing
#               [1,0,0,0,0] UP
#               [0,1,0,0,0] DOWN
#               [0,0,1,0,0] LEFT
#               [0,0,0,1,0] RIGHT
#               [0,0,0,0,1] INTERACT

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
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
        self.held = None
        self.identity = None
        self.set_identity()

    def setAction(self, action):
        self.interacting = False
        self.still = False
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

    def add_score(self, amount):
        self.score += amount
        self.game.score += amount

    def get_position(self):
        return (self.x, self.y)

    def set_identity(self):
        self.identity = id(self)

    def get_identity(self):
        return self.identity

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
        if player.held == None:
            if self.object:
                player.held = self.object
                self.object = None
                self.image = TILE
        else:
            self.object = player.held
            player.held.player = self
            player.held = None
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
        print("TABLE RESET")
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
            Food(player)
                
class PlateDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = PLATE_DISPENSER

    def invoke(self, player):
        if player.held == None:
            Plate(player)

class Pot(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = POT
        self.id = 20
        self.objects = []
        self.time_to_cook = 3
        self.is_cooked = False
    
    def invoke(self, player):
        if (len(self.objects) < 3 and player.held):
            self.objects.append(player.held)
            player.held = None
            if (len(self.objects) == 3):
                self.cook()
        if (self.is_cooked):
            if isinstance(player.held, Plate):
                self.is_cooked = False
                object_id_list = []
                object_id_list.append(player.held.get_owner())
                for ingredient in self.objects:
                    object_id_list.append(ingredient.get_owner())

                player.held = Soup(player, object_id_list)
                self.objects.clear()

    def cook(self):
        self.game.is_cooking = True

    def finish_cook(self):
        self.is_cooked = True
        self.game.is_cooking = False
    
    def update(self):
        self.image = [POT, POT_1, POT_2, POT_3, POT_DONE][len(self.objects) + self.is_cooked]
        self.id = len(self.objects) + self.is_cooked + 20
 
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
            player.add_score(10) 
            # Reward use of ingredients and plate
            for identity in player.held.get_ingredients():
                identity.add_score(5)
                #game.agents[identity].add_score(5)
            player.held = None
            print(game.agentOne.score)
            print(game.agentTwo.score)

class Plate:
    def __init__(self, player):
        self.player = player
        self.player.held = self
        self.full = False
        self.owner = player
    
    def get_owner(self):
        return self.owner

class Food:
    def __init__(self, player):
        self.player = player
        self.player.held = self
        self.owner = player

    def get_owner(self):
        return self.owner

class Soup:
    def __init__(self, player, ingredients):
        self.player = player
        self.player.held = self
        self.ingredients = ingredients
        self.owner = player

    def get_owner(self):
        return self.owner

    def get_ingredients(self):
        return self.ingredients

game = GameSelfPlay('map.csv')
# Set the time interval for the custom event (in milliseconds)
TIME_INTERVAL = 200  # 1 second
# Define a custom event to trigger at the specified time interval
TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, TIME_INTERVAL)
while True:
    game.handle_player_events()
    