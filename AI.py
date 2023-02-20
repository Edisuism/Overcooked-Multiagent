from enum import Enum
import pygame
import sys
import os
from os import path
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# Settings
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255,127,0)

dirname = os.path.dirname(__file__)
TILE = pygame.image.load(dirname + "/Sprites/Obstacle.png")
TILE_FOOD = pygame.image.load(dirname + "/Sprites/Obstacle_food.png")
TILE_PLATE = pygame.image.load(dirname + "/Sprites/Obstacle_plate.png")
TILE_SOUP = pygame.image.load(dirname + "/Sprites/Obstacle_soup.png")
PLATE_DISPENSER = pygame.image.load(dirname + "/Sprites/plate_dispenser.png")
DISPENSER = pygame.image.load(dirname + "/Sprites/food_dispenser.png")
POT = pygame.image.load(dirname + "/Sprites/Pot.png")
POT_1 = pygame.image.load(dirname + "/Sprites/Pot1.png")
POT_2 = pygame.image.load(dirname + "/Sprites/Pot2.png")
POT_3 = pygame.image.load(dirname + "/Sprites/Pot3.png")
POT_DONE = pygame.image.load(dirname + "/Sprites/Pot_done.png")

WIDTH = 448 #1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 320  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Overcooked"
BGCOLOR = DARKGREY

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

class GridWorld:
    def __init__(self, map_data):
        self.grid = []
        self.width = len(map_data[0])
        self.height = len(map_data)
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(map_data[y][x])
            self.grid.append(row)


# Behaviour Tree classes
class Blackboard:
    def __init__(self, map_data):
        self.map_data = map_data

class Node:
    def __init__(self):
        self.status = None
    
    def run(self):
        pass

class Selector(Node):
    def __init__(self, children):
        super().__init__()
        self.children = children
    
    def run(self):
        for child in self.children:
            child.run()
            if child.status == "SUCCESS":
                self.status = "SUCCESS"
                return
        self.status = "FAILURE"

class Sequence(Node):
    def __init__(self, children):
        super().__init__()
        self.children = children
    
    def run(self):
        for child in self.children:
            child.run()
            if child.status == "FAILURE":
                self.status = "FAILURE"
                return
        self.status = "SUCCESS"

class Task(Node):
    def run(self):
        result = self.do_action()
        self.status = "SUCCESS" if result else "FAILURE"
    
    def do_action(self):
        pass

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
        self.id = '1'

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
                self.id = '7'
            if isinstance(self.object, Plate):
                self.image = TILE_PLATE
                self.id = '8'
            if isinstance(self.object, Soup):
                self.image = TILE_SOUP
                self.id = '9'


class FoodDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = (DISPENSER)

    def invoke(self, player):
        if (player.held == None):
            Food(player)
                
class PlateDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = PLATE_DISPENSER

    def invoke(self, player):
        if (player.held == None):
            Plate(player)

class Pot(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = POT
        self.id = '3'
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
                player.held = Soup(player)
                self.objects.clear()

    def cook(self):
        self.game.start_cook(self)

    def finish_cook(self):
        self.is_cooked = True
    
    def update(self):
        self.image = [POT, POT_1, POT_2, POT_3, POT_DONE][len(self.objects) + self.is_cooked]
        if self.image == POT:
            self.id = '3'
        if self.image == POT_1:
            self.id = '10'
        if self.image == POT_2:
            self.id = '11'
        if self.image == POT_3:
            self.id = '12'
        if self.image == POT_DONE:
            self.id = '13'
 

class Counter(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image.fill(LIGHTGREY)
        self.x = x
        self.y = y

    def invoke(self, player):
        if isinstance(player.held, Soup):
            player.add_score(25) 
            player.held = None

# Object classes
class Plate(pygame.sprite.Sprite):
    def __init__(self, player):
        self.game = player.game
        self.player = player
        self.player.held = self
        self.full = False

class Food(pygame.sprite.Sprite):
    def __init__(self, player):
        self.game = player.game
        self.player = player
        self.player.held = self

class Soup(Food):
    def __init__(self, player):
        Food.__init__(self, player)
    

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        groups = game.visible_sprites, game.obstacles
        super().__init__(groups)
        self.game = game
        self.sprites = [pygame.image.load(os.path.dirname(__file__) + f"/Sprites/chef_{name}.png").convert_alpha()
                        for name in ["front", "back", "side", "front_plate", "side_plate", "front_food", "side_food", "front_soup", "side_soup"]]
        self.image = self.sprites[0] 
        self.rect = self.image.get_rect()
        self.x, self.y = x, y
        self.past_x, self.past_y = x, y
        self.orientation = 0
        self.score = 0
        self.held = None

    def add_score(self, amount):
        self.score += amount
        self.game.score += amount

    def get_position(self):
        return (self.x, self.y)

    def move(self, dx=0, dy=0):
        if dx == 1:
            self.orientation = 6
        if dx == -1:
            self.orientation = 4   
        if dy == 1:
            self.orientation = 2
        if dy == -1:
            self.orientation = 8 
        if not self.collide_with_obstacles(dx, dy):
            self.past_x = self.x
            self.past_y = self.y
            self.x += dx
            self.y += dy
            


    def interact(self):
        dx, dy = {6: (1, 0), 4: (-1, 0), 2: (0, 1), 8: (0, -1)}[self.orientation]
        self.use_interactable(dx, dy)

    def collide_with_obstacles(self, dx=0, dy=0):
         return any(obstacle.x == self.x + dx and obstacle.y == self.y + dy for obstacle in self.game.obstacles)

    def use_interactable(self, dx=0, dy=0):
        for interactable in self.game.interactables:
            if interactable.x == self.x + dx and interactable.y == self.y + dy:
                interactable.invoke(self)

    def update(self):
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

    # AI class
class AIPlayer(Player):
    def __init__(self, game, x, y):
        super().__init__(self, game, x, y)
    # prioritises points (1)
    # if there is a cooked dish not held by other player, they will send it to the counter
    # if there is a dish that is cooking, they will stand next to it
    # if there is a pot that is not cooking, they will grab the nearest food and put it in the pot

    # pure support (2)
    # they will simply grab food and place it in the closest available position to the pot
    # after 3 food, they will grab a plate and do the same before returning to positioning food
    def create_plan(self):
            if (self.type == 1):
                if (self.held == Soup):
                    target_x, target_y = self.game.find_closest_object(self.x, self.y, 4)
                    available_x, available_y = self.game.find_closest_object(target_x, target_y, 0) 
                    self.create_path(available_x, available_y)
                elif (self.game.is_number_in_grid(13)):
                    target_x, target_y = self.game.find_closest_object(self.x, self.y, 13) #this will try to path to the pot, but we need them to go to the open tile next to it
                    available_x, available_y = self.game.find_closest_object(target_x, target_y, 0) #repeats the above to find closest open tile. This fails if there is no way to the tile
                    self.create_path(available_x, available_y)
                elif (self.game.is_number_in_grid(12)):
                    target_x, target_y = self.game.find_closest_object(self.x, self.y, 12)
                    available_x, available_y = self.game.find_closest_object(target_x, target_y, 0)
                    self.create_path(available_x, available_y) 
                    if (self.held == None):
                        for obstacle in self.game.obstacles:
                            if (isinstance(obstacle, FoodDispenser)):
                                self.create_path(obstacle.x, obstacle.y)
                else:
                    for obstacle in self.game.obstacles:
                        if (isinstance(obstacle, Table)):
                            if (obstacle.held == None):
                                self.create_path(obstacle.x, obstacle.y)

    def create_path(self, target_x, target_y):
        start_x, start_y = [self.x, self.y]
        start = self.grid.node(start_x, start_y)
        end_x = target_x
        end_y = target_y
        end = self.grid.node(end_x, end_y)
        finder = AStarFinder()
        self.path, = finder.find_path(start, end, self.grid)
        self.grid.cleanup()


