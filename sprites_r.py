import pygame
from settings import *
import os
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Direction(object):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST  = (1, 0)
    WEST  = (-1, 0)


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        groups = game.visible_sprites, game.obstacles
        super().__init__(groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        dirname = os.path.dirname(__file__)
        self.sprites = [pygame.image.load(dirname + "/Sprites/chef_front.png").convert_alpha(), #0
                        pygame.image.load(dirname + "/Sprites/chef_back.png").convert_alpha(), #1
                        pygame.image.load(dirname + "/Sprites/chef_side.png").convert_alpha(), #2
                        pygame.image.load(dirname + "/Sprites/chef_front_plate.png").convert_alpha(), #3
                        pygame.image.load(dirname + "/Sprites/chef_side_plate.png").convert_alpha(), #4
                        pygame.image.load(dirname + "/Sprites/chef_front_food.png").convert_alpha(), #5
                        pygame.image.load(dirname + "/Sprites/chef_side_food.png").convert_alpha(), #6
                        pygame.image.load(dirname + "/Sprites/chef_front_soup.png").convert_alpha(), #7
                        pygame.image.load(dirname + "/Sprites/chef_side_soup.png").convert_alpha()]  #8
        self.image = self.sprites[0] 
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.orientation = 0
        self.score = 0
        self.held = None

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
            self.x += dx
            self.y += dy

    def interact(self):
        if self.orientation == 6:
            self.use_interactable(1,0)
        if self.orientation == 4:
            self.use_interactable(-1,0)
        if self.orientation == 2:
            self.use_interactable(0,1)
        if self.orientation == 8:
            self.use_interactable(0,-1)


    def collide_with_obstacles(self, dx=0, dy=0):
        for obstacle in self.game.obstacles:
            if obstacle.x == self.x + dx and obstacle.y == self.y + dy:
                return True
        return False

    def use_interactable(self, dx=0, dy=0):
        for interactable in self.game.interactables:
            if interactable.x == self.x + dx and interactable.y == self.y + dy:
                interactable.invoke(self)
        return False

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

    def add_score(self, amount):
        self.score += amount
        self.game.score += amount

    def get_position(self):
        return (self.x, self.y)

class Cooperative:
    def __init__(self, game, x, y, matrix):
        groups = game.visible_sprites, game.obstacles
        super().__init__(groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        dirname = os.path.dirname(__file__)
        self.sprites = [pygame.image.load(dirname + "/Sprites/chef_front.png").convert_alpha(), #0
                        pygame.image.load(dirname + "/Sprites/chef_back.png").convert_alpha(), #1
                        pygame.image.load(dirname + "/Sprites/chef_side.png").convert_alpha(), #2
                        pygame.image.load(dirname + "/Sprites/chef_front_plate.png").convert_alpha(), #3
                        pygame.image.load(dirname + "/Sprites/chef_side_plate.png").convert_alpha(), #4
                        pygame.image.load(dirname + "/Sprites/chef_front_food.png").convert_alpha(), #5
                        pygame.image.load(dirname + "/Sprites/chef_side_food.png").convert_alpha(), #6
                        pygame.image.load(dirname + "/Sprites/chef_front_soup.png").convert_alpha(), #7
                        pygame.image.load(dirname + "/Sprites/chef_side_soup.png").convert_alpha()]  #8
        self.image = self.sprites[0] 
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.orientation = 0
        self.score = 0
        self.held = None

        pathfinding_matrix = [
            [0,0,0,0,0,0,0],
            [0,1,1,1,1,1,0],
            [0,1,1,1,1,1,0],
            [0,1,1,1,1,1,0],
            [0,0,0,0,0,0,0]]

        #pathfinding_grid = Grid(matrix= pathfinding_matrix)

        self.type = 1 #personality / plan, will adjust during game based on player
        self.matrix = matrix
        self.grid = Grid(matrix = matrix)
        self.target = []
        self.path = []

    def create_plan(self):
        if (self.type == 1):
            if (self.held == None):
                for obstacle in self.game.obstacles:
                    if (isinstance(obstacle, FoodDispenser)):
                        self.create_path(obstacle.x, obstacle.y)
            else:
                for obstacle in self.game.obstacles:
                    if (isinstance(obstacle, Obstacle)):
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
            self.x += dx
            self.y += dy

    def interact(self):
        if self.orientation == 6:
            self.use_interactable(1,0)
        if self.orientation == 4:
            self.use_interactable(-1,0)
        if self.orientation == 2:
            self.use_interactable(0,1)
        if self.orientation == 8:
            self.use_interactable(0,-1)


    def collide_with_obstacles(self, dx=0, dy=0):
        for obstacle in self.game.obstacles:
            if obstacle.x == self.x + dx and obstacle.y == self.y + dy:
                return True
        return False

    def use_interactable(self, dx=0, dy=0):
        for interactable in self.game.interactables:
            if interactable.x == self.x + dx and interactable.y == self.y + dy:
                interactable.invoke(self)
        return False

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
            


class Interactable(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.visible_sprites, game.obstacles, game.interactables
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pygame.Surface((TILESIZE, TILESIZE))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def invoke(self):
        pass

    def get_position(self):
        return (self.x, self.y)


class Obstacle(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = (TILE)
        self.object = None

    def invoke(self, player):
        if (player.held == None):
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
            if isinstance(self.object, Plate):
                self.image = TILE_PLATE
            if isinstance(self.object, Soup):
                self.image = TILE_SOUP
                

class PlateDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = PLATE_DISPENSER

    def invoke(self, player):
        if (player.held == None):
            Plate(player)


class Plate(pygame.sprite.Sprite):
    def __init__(self, player):
        self.game = player.game
        self.player = player
        self.player.held = self
        self.full = False


class FoodDispenser(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = (DISPENSER)

    def invoke(self, player):
        if (player.held == None):
            Food(player)


class Food(pygame.sprite.Sprite):
    def __init__(self, player):
        self.game = player.game
        self.player = player
        self.player.held = self
    

class Soup(Food):
    def __init__(self, player):
        Food.__init__(self, player)
    

class Pot(Interactable):
    def __init__(self, game, x, y):
        Interactable.__init__(self, game, x, y)
        self.image = POT
        self.objects = []
        self.time_to_cook = 3
        self.is_cooked = False
        self.x = x
        self.y = y
    
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
        if (len(self.objects) == 0):
            self.image = POT
        if (len(self.objects) == 1):
            self.image = POT_1
        if (len(self.objects) == 2):
            self.image = POT_2
        if (len(self.objects) == 3):
            self.image = POT_3
        if self.is_cooked:
            self.image = POT_DONE


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

