import pygame
import os

# define some colors (R, G, B)
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

# game settings
WIDTH = 384 #1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 320  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Overcooked"
BGCOLOR = DARKGREY

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE


# gameplay data
object_data = {
    'onion': {'graphic': '../graphics'},
    'plate': {'graphic': '../graphics'}
}
# fixed timestep in milliseconds
TIME_STEP = 50  
cooking_time = 50
