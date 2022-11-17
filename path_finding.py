#
# A* path finding algortihm
#
# --------------------------------------------------------------------------------
# Imports

import random
import os
import tkinter as tk
from tkinter import messagebox

from settings import *

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

class Setup:
    
    def __init__(self):

        # Game window
        self.win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Number of x and y squares
        self.sq_x = math.floor(WIDTH/SIZE)
        self.sq_y = math.floor(HEIGHT/SIZE)

        self.game_rects = [[0] * self.sq_x for _ in range(self.sq_y)]
        self.grid = [[0] * self.sq_x for _ in range(self.sq_y)]
        
        for i in range(self.sq_x):
            for j in range(self.sq_y):
                self.grid[i][j] = Spot(i, j)
                self.game_rects[i][j] = pygame.Rect(i*SIZE, j*SIZE, SIZE, SIZE)
        
        # Initialize start and end point
        self.start = 0
        self.end = 0

        # Open, closed, parent and neighbor arrays
        self.open = []
        self.closed = []
        self.parent = []

        # While loop variables
        self.dragged = False

    def run(self):
        # Init start/end counter and draw the background
        self.counter = 0
        self.init_draw()
        
        # Main loop
        self.calculating = True
        while self.calculating:
            self.clock.tick(FPS)
            pygame.display.flip()
            self.events()
    
    def events(self):
        for event in pygame.event.get():

            # Exit when pressing X
            if event.type == pygame.QUIT:
                if self.calculating:
                    self.calculating = False
                    pygame.quit()
                    # quit()

            # Start game when pressing Enter
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.try_start()

            # Mouse button down events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()

                # Start and end point
                for i in range(self.sq_x):
                    for j in range(self.sq_y):
                        if self.game_rects[i][j].collidepoint(pos):
                            if self.counter == 0:
                                self.draw_points('start', i, j, BLUE)
                            elif self.counter == 1:
                                self.draw_points('end', i, j, GREEN)

                # Start button
                if self.start_button_rect.collidepoint(pos):
                    self.try_start()

                # Reset button
                if self.reset_button_rect.collidepoint(pos):
                    self.counter = 0
                    main()

                # Generate random maze buttons
                self.maze_collision(self.maze1_rect, pos, 1)
                self.maze_collision(self.maze2_rect, pos, 2)
                self.maze_collision(self.maze3_rect, pos, 3)

            # Place walls
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                self.place_wall()
                self.dragged = True

            if event.type == pygame.MOUSEMOTION and self.dragged:
                self.place_wall()             

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                self.dragged = False

#----- Help functions --------------------------------------------------------------------

    # Draw the start screen     
    def init_draw(self):
        
        # Background
        self.win.fill(BG)

        # Grid
        for i in range(self.sq_x):
            for j in range(self.sq_y):
                x, y = self.grid[i][j].i, self.grid[i][j].j
                pygame.draw.rect(self.win, GAME_COLOR, (x*SIZE, y*SIZE, SIZE, SIZE), THICKNESS)

        # Lines dividing board from button area
        pygame.draw.line(self.win, WHITE, (self.sq_x*SIZE, 0), (self.sq_x*SIZE, HEIGHT), THICKNESS)
        pygame.draw.line(self.win, BLACK, (self.sq_x*SIZE+THICKNESS*2, 0), (self.sq_x*SIZE+THICKNESS*2, HEIGHT), THICKNESS*4)

        # Text on screen
        self.start_button_text, self.start_button_rect = self.create_text('Start algorithm', WIN_HEIGHT - 100)
        self.reset_button_text, self.reset_button_rect = self.create_text('Reset', WIN_HEIGHT - 50)
        self.maze1_text, self.maze1_rect = self.create_text('Random maze 40%', 75)
        self.maze2_text, self.maze2_rect = self.create_text('Random maze 50%', 125)
        self.maze3_text, self.maze3_rect = self.create_text('Random maze 60%', 175)

    # Create text and rounded text rectangles and draw on screen
    def create_text(self, text, y):
        text = OPT_FONT.render(text, True, WHITE, BLACK)
        rect = text.get_rect()
        rect.center = ((WIN_WIDTH + WIDTH)/2, y)
        
        x, y, w, h = rect[0], rect[1], rect[2], rect[3]
        for i in [4, 2, 0]:
            self.rounded(self.win, (x-(4+i), y-(3+i), w+(8+2*i), h+(6+2*i)), SHADING[int(i/2)], RADIUS)
        self.win.blit(text, rect)
        
        return text, rect

    # Check if start and end point is selected
    def try_start(self):
        if self.counter == 0:
            self.point_error_message()
        elif self.counter == 1:
            self.point_error_message()
        elif self.counter >= 2:
            self.calc()

    # Maze button collisions
    def maze_collision(self, maze, pos, n):
        if maze.collidepoint(pos):
            self.counter = 0
            for i in range(self.sq_x):
                for j in range(self.sq_y):
                    self.grid[i][j] = Spot(i, j)
            self.generate_maze(n)

    # Draw start, end, or wall points
    def draw_points(self, kind, i, j, color):
        draw = False
        if kind == 'start' and self.grid[i][j].wall == False:
            self.start = self.grid[i][j]
            draw = True
            self.counter += 1
        elif kind == 'end' and self.grid[i][j].wall == False:
            self.end = self.grid[i][j]
            draw = True
            self.counter += 1
        elif kind == 'wall' and self.grid[i][j] != self.start and self.grid[i][j] != self.end:
            self.grid[i][j].wall = True
            draw = True

        if draw:    
            rect = pygame.Rect(self.grid[i][j].i*SIZE + 1, self.grid[i][j].j*SIZE + 1, SIZE - 2, SIZE - 2)
            pygame.draw.rect(self.win, color, rect)

    def place_wall(self):
        pos = pygame.mouse.get_pos()
        for i in range(self.sq_x):
            for j in range(self.sq_y):
                if self.game_rects[i][j].collidepoint(pos):
                    self.draw_points('wall', i, j, BLACK)

    # Generate random maze with 40, 50 or 60% chance of a square becoming a wall
    def generate_maze(self, n):
        self.init_draw()
        RANDOM_MAZE = 0.3 + (n * 0.1)
            
        for i in range(self.sq_x):
            pygame.display.flip()
            for j in range(self.sq_y):
                r = random.uniform(0, 1)
                if r < RANDOM_MAZE:
                    self.draw_points('wall', i, j, BLACK)
        
    # Rounded corners on rectangles
    def rounded(self, surface, rect, color, radius=0.4):       
        rect = pygame.Rect(rect)
        color = pygame.Color(*color)
        alpha = color.a
        color.a = 0
        pos = rect.topleft
        rect.topleft = (0, 0)
        rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

        circle = pygame.Surface([min(rect.size)*3]*2, pygame.SRCALPHA)
        pygame.draw.ellipse(circle, BLACK, circle.get_rect(), 0)
        circle = pygame.transform.smoothscale(circle, [int(min(rect.size)*radius)]*2)

        radius = rectangle.blit(circle, rect.topleft)
        radius.topright = rect.topright
        rectangle.blit(circle, radius)
        radius.bottomright = rect.bottomright
        rectangle.blit(circle, radius)
        radius.bottomleft = rect.bottomleft
        rectangle.blit(circle, radius)

        rectangle.fill(BLACK, rect.inflate(-radius.w, 0))
        rectangle.fill(BLACK, rect.inflate(0, -radius.h))

        rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)

        surface.blit(rectangle, pos)

    def point_error_message(self):
        tk.Tk().withdraw()
        if self.counter == 0:
            messagebox.showinfo('Error', 'Please place a start and an end point.')
        elif self.counter == 1:
            messagebox.showinfo('Error', 'Please place an end point.')
 

        
# ---------------------------------------------------------------------------
# A* algorithm calculation

    # Calculate
    def calc(self):
        self.start.g = 0
        self.start.f = self.start.h
        self.open.append(self.start)
        
        path = 0
        
        while len(self.open) > 0:

            # Be able to use buttons during calculation
            self.events()
            
            # Current is the object with minimum f-value in open list
            current = min(self.open, key=lambda x: x.f)

            # If current is end, then finish algorithm and print the path
            if current == self.end:
                path = self.create_path(current)
                self.draw_path(path)
                self.open = []
                self.end_message('Path found!', ' It took ' + str(len(path)-1) + ' steps to reach the end. \n\n Do you want to simulate again?')
                self.calculating = False
                break

            # Remove current from open list and add to closed list
            self.open.remove(current)
            self.closed.append(current)

            # Neighbors: Only add neighbors that are within the grid and are not a wall
            neighbors = []
            for i in range(len(NEIGHBORS)):
                next_x = current.i + NEIGHBORS[i][0]
                next_y = current.j + NEIGHBORS[i][1]
                if next_x >= 0 and next_x <= self.sq_x - 1 and next_y >= 0 and next_y <= self.sq_y - 1 and self.grid[next_x][next_y].wall == False:
                    neighbors.append(self.grid[next_x][next_y])

            # Check every neighbor that hasn't been checked before
            for neighbor in neighbors:
                if neighbor not in self.closed:
                    tentative_g = current.g + self.dis(current, neighbor)
                    
                    # Update neighbor f, g, and h score if we find a better neighbor
                    if tentative_g < neighbor.g:
                        neighbor.parent = current
                        neighbor.g = tentative_g
                        neighbor.h = self.h(neighbor)
                        neighbor.f = neighbor.g + neighbor.h
                        
                        # Visualize the thinking process if grid size is
                        self.clock.tick(FPS_PROCESS)
                        self.draw_progress(neighbor, current)

                        # Add neighbor to open list for later evaluation
                        if neighbor not in self.open:
                            self.open.append(neighbor)
            
        # There is no available path if there are no items in open list and the path has not been found   
        if path == 0:
            self.end_message('No path found!', ' There is no path from start to end point. \n\n Do you want to simulate again?')
            self.calculating = False

# ------ A* help functions --------------------------------------------

    # Create the path
    def create_path(self, current):
        total_path = []
        while current.parent != 0:
            total_path.append(current)
            current = current.parent
        total_path.append(self.start)
        return total_path
    
    # Distance from current to neighbor. If neighbor is diagnoal to current node, distance is approximately 1.4 (sqrt(2)), else 1.
    def dis(self, current, neighbor):
        dx = abs(current.i - neighbor.i)
        dy = abs(current.j - neighbor.j)
        if dx and dy != 0:
            return 1.4 
        return 1

    # Estimate distance from neighbor node to end by a straight line between end point and neighbor (dx + dy) or Chebyshev distance heuristic: (D1 * (dx + dy) + (D2 - 2 * D1) * min(dx, dy))
    def h(self, neighbor):
        D1, D2 = 1, 2
        dx, dy = abs(self.end.i - neighbor.i), abs(self.end.j - neighbor.j)
        return dx + dy

    # Print thinking process. If statement to make sure that start and end node is left untouched
    def draw_progress(self, neighbor, current):
        kind = [neighbor, current]
        for k in range(2):
            x, y = kind[k].i, kind[k].j
            rect = pygame.Rect(x*SIZE + 1, y*SIZE + 1, SIZE - 2, SIZE - 2)
            if (x, y) not in [(self.start.i, self.start.j), (self.end.i, self.end.j)]:
                pygame.draw.rect(self.win, THINKING_COLOR[k], rect)
        
        pygame.display.flip()
        
    # Print the winning path
    def draw_path(self, path):
        for spot in reversed(path):
            self.clock.tick(FPS_WIN)
            x, y = spot.i, spot.j
            rect = pygame.Rect(x*SIZE+1, y*SIZE+1, SIZE-2, SIZE-2)
            pygame.draw.rect(self.win, BLUE, rect)
            pygame.display.flip()

    # End messages
    def end_message(self, title, text):
        tk.Tk().withdraw()
        answer = messagebox.askquestion(title, text)
        if answer == 'yes':
            self.counter = 0
            main()
        pygame.quit()

# ---------------------------------------------------------------------------
# Spot object
# ---------------------------------------------------------------------------

class Spot:

    def __init__(self, i, j):
        self.i = i
        self.j = j
        self.f = math.inf
        self.g = math.inf
        self.h = 0
        self.wall = False
        self.parent = 0

# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

def main():
    Setup().run()

# Initialize window and run main script
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
pygame.mixer.init()

main() 
