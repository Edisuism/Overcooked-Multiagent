import enum
import pygame
import sys
from settings import *
#from sprites_r import *
from AI import *
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
        self.map_data = []
        self.player = []
        self.playing = True
        self.load_data('map.csv')
        self.start_time = pygame.time.get_ticks()

        self.counter = None
        self.pot = None
        self.is_cooking = False
        self.score = 0
        self.game_length = 20
        self.cook_time = 3
        self.cook_counter = 3
        self.start_counter = 0
        self.gameover = False

    def load_data(self, FILENAME):
        game_folder = path.dirname(__file__)
        with open(path.join(game_folder, FILENAME), 'r') as file:
            reader = csv.reader(file)
            for line in reader:
                self.map_data.append(line) 

    def create_map(self):
        # enumerate gives us index and the item
        for row, tiles in enumerate(self.map_data):
            for col, tile in enumerate(tiles):
                if tile == '0':
                    self.player.append(Player(self, col, row))
                if tile == '1':
                    Table(self, col, row)
                if tile == '2':
                    PlateDispenser(self, col, row)
                if tile == '3':
                    self.pot = Pot(self, col, row)
                if tile == '4':
                    self.counter = Counter(self, col, row)
                if tile == '5':
                    FoodDispenser(self, col, row)
                # if tile == '6':
                #     AIPlayer(self, col, row)
                grid_world = GridWorld(self.map_data)


# ___Update___
    def run(self):
        while self.playing:
            self.events()
            # self.ai()
            self.update()
            self.draw()
    
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

                # if self.player.count == 1:
                #     break

                # if event.key == pygame.K_a:
                #     self.player[1].move(dx=-1)
                # if event.key == pygame.K_d:
                #     self.player[1].move(dx=1)
                # if event.key == pygame.K_w:
                #     self.player[1].move(dy=-1)
                # if event.key == pygame.K_s:
                #     self.player[1].move(dy=1)
                # if event.key ==pygame.K_e:
                #     self.player[1].interact()

    # def ai_update(self):
    #     pathfinding_matrix = [
    #     [0,0,0,0,0,0,0],
    #     [0,1,1,1,1,1,0],
    #     [0,1,1,1,1,1,0],
    #     [0,1,1,1,1,1,0],
    #     [0,0,0,0,0,0,0]]

    #     pathfinding_grid = Grid(matrix= pathfinding_matrix)

    #     self.type = 1 
    #     self.matrix = matrix
    #     self.grid = Grid(matrix = matrix)
    #     self.target = []
    #     self.path = []

    #     if isinstance(self.player[1].held, Soup):
    #         target = self.counter
    #     elif self.pot.is_cooked:
    #         target = self.pot
    #     elif len(self.pot.objects) < 3:
    #         pass #closest food dispenser



    # def create_plan(self):
    #     if (self.type == 1):
    #         if (self.held == None):
    #             for obstacle in self.game.obstacles:
    #                 if (isinstance(obstacle, FoodDispenser)):
    #                     self.create_path(obstacle.x, obstacle.y)
    #         else:
    #             for obstacle in self.game.obstacles:
    #                 if (isinstance(obstacle, Obstacle)):
    #                     if (obstacle.held == None):
    #                         self.create_path(obstacle.x, obstacle.y)

    # def create_path(self, target_x, target_y):
    #     start_x, start_y = [self.x, self.y]
    #     start = self.grid.node(start_x, start_y)
    #     end_x = target_x
    #     end_y = target_y
    #     end = self.grid.node(end_x, end_y)
    #     finder = AStarFinder()
    #     self.path, = finder.find_path(start, end, self.grid)
    #     self.grid.cleanup()


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

    def start_cook(self, pot):
        self.pot = pot
        self.is_cooking = True

    def stop_cook(self):
        self.is_cooking = False
        self.cook_counter = self.cook_time
        self.pot.finish_cook()

    def restart(self):
        self.visible_sprites.empty()
        self.obstacles.empty()
        self.interactables.empty()
        self.map_data.clear()
        self.player.clear()
        self.playing = True
        self.load_data('map.txt')

        self.pot = None
        self.is_cooking = False
        self.score = 0
        self.cook_counter = 3
        self.start_counter = 0
        self.gameover = False
        self.create_map()


game = Game()
game.create_map()
while True:
    # game.create_map()
    game.run()