import pygame
import sys
import math
import copy
from settings import *
from AI import *
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
        self.AIplayer = None
        self.table = []
        self.pot = []
        self.playing = True
        self.grid = []
        self.AIgrid = []
        self.pathfinding_matrix = None
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
            self.grid = []
            for line in reader:
                # Convert each value to an integer and append to grid
                row = [int(value) for value in line]
                self.grid.append(row) 

    def create_map(self):
        for row_index, row in enumerate(self.grid):
            for col_index, tile in enumerate(row):
                if tile == 0:
                    pass
                elif tile == 1:
                    self.table.append(Table(self, col_index, row_index))
                elif tile == 2:
                    (PlateDispenser(self, col_index, row_index))
                elif tile == 3:
                    self.pot.append(Pot(self, col_index, row_index))
                elif tile == 4:
                    (Counter(self, col_index, row_index))
                elif tile == 5:
                    (FoodDispenser(self, col_index, row_index))
                elif tile == 6:
                    self.player.append(Player(self, col_index, row_index))
                elif tile == 20:
                    self.AIplayer = AIPlayer(self, col_index, row_index)


# helper functions for grid
    def find_surrounding(self, x, y, targetObject):
        # flip grid to better align with pathfinding matrix
        flipped_grid = []
        for j in range(len(self.grid[0])):
            new_row = []
            for i in range(len(self.grid)):
                new_row.append(self.grid[i][j])
            flipped_grid.append(new_row)

        m = len(flipped_grid)
        n = len(flipped_grid[0])
        minDistance = math.inf
        for i in range(m):
            for j in range(n):
                #print(i, j)
                if flipped_grid[i][j] == targetObject:
                    distance = math.sqrt((x - i)**2 + (y - j)**2)
                    if distance < minDistance:
                        minDistance = distance
                        closestObject_x = i
                        closestObject_y = j
                        #print("Found object at", i, j )
        return closestObject_x, closestObject_y


    def find_closest_objects(self, x, y, targetObject):
        print("TargetObject", targetObject)
        flipped_grid = []
        for j in range(len(self.grid[0])):
            new_row = []
            for i in range(len(self.grid)):
                new_row.append(self.grid[i][j])
            flipped_grid.append(new_row)
        
        m = len(flipped_grid)
        n = len(flipped_grid[0])
        minDistance = math.inf

        if (targetObject == 3 or targetObject == 10 or targetObject == 11 or targetObject == 12):
            target_objects = [3, 10, 11, 12]

            for i in range(m):
                for j in range(n):
                    if flipped_grid[i][j] in target_objects:
                        print("FOUND TARGET")
                        distance = math.sqrt((x - i)**2 + (y - j)**2)
                        if distance < minDistance:
                            minDistance = distance
                            closestObject_x = i
                            closestObject_y = j
            return closestObject_x, closestObject_y

        for i in range(m):
            for j in range(n):
                if flipped_grid[i][j] == targetObject:
                    print("FOUND TARGET")
                    distance = math.sqrt((x - i)**2 + (y - j)**2)
                    if distance < minDistance:
                        minDistance = distance
                        closestObject_x = i
                        closestObject_y = j
        return closestObject_x, closestObject_y

    def find_closest_object(self, x, y, targetObject):
        # flip grid to better align with pathfinding matrix
        print("TargetObject", targetObject)
        flipped_grid = []
        for j in range(len(self.grid[0])):
            new_row = []
            for i in range(len(self.grid)):
                new_row.append(self.grid[i][j])
            flipped_grid.append(new_row)
        
        m = len(flipped_grid)
        n = len(flipped_grid[0])
        minDistance = math.inf

        if (targetObject == 3 or targetObject == 10 or targetObject == 11 or targetObject == 12):
            print("TRUE")
            print("MINDIST", minDistance)
            target_objects = [3, 10, 11, 12]

            for i in range(m):
                for j in range(n):
                    #print(i, j)
                    if flipped_grid[i][j] in target_objects:
                        print("FOUND")
                        if self.are_surrounding_tiles_free(i,j):
                            k,l = self.are_surrounding_tiles_free(i,j)
                            distance = math.sqrt((x - k)**2 + (y - l)**2)
                            if distance < minDistance:
                                minDistance = distance
                                closestObject_x = k
                                closestObject_y = l
            return closestObject_x, closestObject_y

        for i in range(m):
            for j in range(n):
                #print(i, j)
                if flipped_grid[i][j] == targetObject:
                    if self.are_surrounding_tiles_free(i,j):
                        k,l = self.are_surrounding_tiles_free(i,j)
                        distance = math.sqrt((x - k)**2 + (y - l)**2)
                        if distance < minDistance:
                            minDistance = distance
                            closestObject_x = k
                            closestObject_y = l
                            #print("Found object at", k, l )
        return closestObject_x, closestObject_y
        # m = len(self.grid)
        # n = len(self.grid[0])
        # minDistance = math.inf
        # for i in range(m):
        #     for j in range(n):
        #         print(i, j)
        #         if self.grid[i][j] == targetObject:
        #             distance = math.sqrt((x - i)**2 + (y - j)**2)
        #             if distance < minDistance:
        #                 minDistance = distance
        #                 closestObject_x = i
        #                 closestObject_y = j
        #                 print("Found object at", i, j )
        #return closestObject_x, closestObject_y

    def is_number_in_grid(self, number):
        for row in self.grid:
            if number in row:
                return True
        return False
    
    def are_surrounding_tiles_free(self, x, y):
        # if self.grid[x][y] == 0:
        #     return x, y
        
        # for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        #     if x+dx >= 0 and x+dx < len(self.grid) and y+dy >= 0 and y+dy < len(self.grid[0]):
        #         if self.grid[x+dx][y+dy] == 0:
        #             return x+dx, y+dy
        if self.grid[y][x] == 0:
            return x, y
        
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if x+dx >= 0 and x+dx < len(self.grid[0]) and y+dy >= 0 and y+dy < len(self.grid):
                if self.grid[y+dy][x+dx] == 0:
                    print("SURROUNDING", x+dx, y+dy)
                    return x+dx, y+dy
        print("NO SURROUNDING")

    def pathtest(self , startx, starty, targetx, targety):
        # create copy of grid for AI purpose
        self.AIgrid = copy.deepcopy(self.grid)
        for row in range(len(self.AIgrid)):
            for col in range(len(self.AIgrid[row])):
                cell_value = self.AIgrid[row][col]
                if (cell_value > 0):
                    self.AIgrid[row][col] = cell_value * -1
                if (cell_value == 0):
                    self.AIgrid[row][col] = 1
        self.visualise_grid(self.grid)
        self.visualise_grid(self.AIgrid) ##
        self.pathfinding_matrix = Grid(matrix=self.AIgrid)
        print("Pathfinding")
        print(self.pathfinding_matrix.grid_str())
        start = self.pathfinding_matrix.node(startx, starty)
        end = self.pathfinding_matrix.node(targetx, targety)
        finder = AStarFinder(diagonal_movement=False)
        path, runs = finder.find_path(start, end, self.pathfinding_matrix)
        self.pathfinding_matrix.cleanup()
        print('Path:', path)
        #print('Runs:', runs)
        #self.visualise_grid(self.pathfinding_matrix)

        return path


# ___Update___
    def run(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
            #self.visualise_grid()
    
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

            self.AIplayer.ai_update()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quit()
                if event.key == pygame.K_r:
                    self.restart()
                if event.key == pygame.K_k:
                    self.pathtest(1,1,5,1)
                    # f_x, f_y = self.find_closest_object(3,3,4)
                    # print("X-coordinate: " + f_x)
                    # print("Y-coordinate: " + f_y)
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
                self.visualise_grid(self.grid)


    def update_grid(self):
        for player in self.player:
            #invert x and y to fit with gridworld
            self.grid[player.past_y][player.past_x] = 0
            self.grid[player.y][player.x] = 6

        self.grid[self.AIplayer.past_y][self.AIplayer.past_x] = 0
        self.grid[self.AIplayer.y][self.AIplayer.x] = 20

        for table in self.table:
            self.grid[table.y][table.x] = table.id

        for pot in self.pot:
            self.grid[pot.y][pot.x] = pot.id

    def visualise_grid(self , grid):
        #print(*self.grid, sep='\n')# Define the labels for the rows and columns
        # print("{:<6}".format(""), end="")
        # for col in range(len(grid[0])):
        #     print("{:<6}".format(f"Col {col}"), end="")
        # print()
        # for row in range(len(grid)):
        #     print("{:<6}".format(f"Row {row}"), end="")
        #     for col in range(len(grid[row])):
        #         print("{:<6}".format(str(grid[row][col])), end="")
        #     print()
        print("{:<5}".format(""), end="|")
        for col in range(len(grid[0])):
            print("{:^5}".format(f"Col {col}"), end="|")
        print("\n" + "-"*len("{:<5}".format("")) + "-"*(6*len(grid[0])+1))
        for row in range(len(grid)):
            print("{:<5}".format(f"Row {row}"), end="|")
            for col in range(len(grid[row])):
                print("{:^5}".format(str(grid[row][col])), end="|")
            print("\n" + "-"*len("{:<5}".format("")) + "-"*(6*len(grid[row])+1))


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


