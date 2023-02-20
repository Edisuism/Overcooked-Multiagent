import enum
import pygame
import sys
import math
from settings import *
from AI import *
#from sprites_r import *
import os
import csv
from os import path
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

class Game:
    # ___Init___

    def __init__(self):
        # game settings
        pygame.init()
        pygame.display.set_caption(TITLE)
        pygame.key.set_repeat(500, 100)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 50)
        self.cook_font = pygame.font.SysFont(None, 25)
        self.timer_event = pygame.USEREVENT+1
        pygame.time.set_timer(self.timer_event, 1000)

        # gameplay variables
        self.visible_sprites = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()
        self.interactables = pygame.sprite.Group()
        self.player = []
        self.table = []
        self.pot = []
        self.playing = True
        self.grid = []
        self.load_grid_from_csv('map copy.csv')
        self.start_time = pygame.time.get_ticks()

        self.counter = None
        self.is_cooking = False
        self.score = 0
        self.game_length = 20
        self.cook_time = 3
        self.cook_counter = 3
        self.start_counter = 0
        self.gameover = False

    def load_grid_from_csv(self, FILENAME):
        game_folder = path.dirname(__file__)
        with open(path.join(game_folder, FILENAME), 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                self.grid.append(line) 

    def create_map(self):
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                if tile == 0:
                    pass
                elif tile == '1':
                    self.table.append(Table(self, col_index, row_index))
                elif tile == '2':
                    (PlateDispenser(self, col_index, row_index))
                elif tile == '3':
                    self.pot.append(Pot(self, col_index, row_index))
                elif tile == '4':
                    (Counter(self, col_index, row_index))
                elif tile == '5':
                    (FoodDispenser(self, col_index, row_index))
                elif tile == '6':
                    self.player.append(Player(self, col_index, row_index))

# helper functions for grid
    def find_closest_object(self, x, y, targetObject):
        m = len(self.grid)
        n = len(self.grid[0])
        minDistance = math.inf
        closestObject = None
        for i in range(m):
            for j in range(n):
                if self.grid[i][j] == targetObject:
                    distance = math.sqrt((x - i)**2 + (y - j)**2)
                    if distance < minDistance:
                        minDistance = distance
                        closestObject = self.grid[i][j]
        return closestObject

    def is_number_in_grid(self, number):
        for row in self.grid:
            if number in row:
                return True
        return False

# ___Update___
    def run(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
            self.visualise_grid()
    
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_r:
                    self.restart()
            
            if self.gameover:
                break

            if event.type == self.timer_event:
                self.start_counter -=1
                if self.is_cooking:
                    self.cook_counter-=1
                    if self.cook_counter <= 0:
                        self.stop_cook()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_r:
                    self.restart()
                if event.key == pygame.K_LEFT:
                    self.player[0].move(dx=-1)
                if event.key == pygame.K_RIGHT:
                    self.player[0].move(dx=1)
                if event.key == pygame.K_UP:
                    self.player[0].move(dy=-1)
                if event.key == pygame.K_DOWN:
                    self.player[0].move(dy=1)
                if event.key == pygame.K_RCTRL:
                    self.player[0].interact()
                self.update_grid()


    def update_grid(self):
        for player in self.player:
            #invert x and y to fit with gridworld
            self.grid[player.past_y][player.past_x] = '0'
            self.grid[player.y][player.x] = '6'

        for table in self.table:
            self.grid[table.y][table.x] = table.id

        for pot in self.pot:
            self.grid[pot.y][pot.x] = pot.id

    def visualise_grid(self):
        print(*self.grid, sep='\n')

    def update(self):
        self.visible_sprites.update()

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.visible_sprites.draw(self.screen)
        self.draw_UI()
        pygame.display.flip()


    def draw_UI(self):
                # score
                self.text = self.font.render("Score: " + str(self.score), True, (255, 0, 0))
                text_rect = self.text.get_rect(topright = self.screen.get_rect().topright)
                self.screen.blit(self.text, text_rect)

                # timer
                if self.start_counter + self.game_length < self.game_length and self.start_counter + self.game_length > 0:
                    self.text = self.font.render("Time: " + str(self.start_counter + self.game_length), True, (255, 0, 0))
                    text_rect = self.text.get_rect(topleft = self.screen.get_rect().topleft)
                    self.screen.blit(self.text, text_rect)
                elif self.start_counter + self.game_length > 0:
                    self.text = self.font.render("Time: " + str(self.game_length), True, (255, 0, 0))
                    text_rect = self.text.get_rect(topleft = self.screen.get_rect().topleft)
                    self.screen.blit(self.text, text_rect)
                if self.start_counter + self.game_length <= 0:
                    self.text = self.font.render("Game Finished!", True, (255, 0, 0))
                    text_rect = self.text.get_rect(topleft = self.screen.get_rect().topleft)
                    self.screen.blit(self.text, text_rect)
                    self.gameover = True
                
                # countdown to start
                if self.start_counter > 0:
                    self.text = self.font.render(str(self.start_counter), True, (255, 0, 0))
                    text_rect = self.text.get_rect(center = self.screen.get_rect().center)
                    self.screen.blit(self.text, text_rect)

                # cooking timer (currently only supports 1 pot)
                if self.is_cooking:
                    self.text = self.cook_font.render(str(self.cook_counter), True, (255, 0, 0))
                    text_rect = self.pot.rect
                    self.screen.blit(self.text, text_rect)

    def draw_grid(self):
        # this is not necessary, just draws the grid lines
        for x in range(0, WIDTH, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pygame.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))
        pass


game = Game()
game.create_map()
while True:
    game.run()


