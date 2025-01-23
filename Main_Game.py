import pygame
import random
from queue import PriorityQueue
import time
import sqlite3

class maze():

    WIDTH = 1300        #this is the width of the pygame window
    HEIGHT = 800        #this is the height of the pygame window
    RED = (255, 0, 0)       
    PURPLE = (128, 0, 128)      #RGB colour for red, represented as a tuple data structure
    BLACK = (0,0,0)             #RGB colour for black, represented as a tuple data structure
    GREEN = (51,184,100)        #RGB colour for green, represented as a tuple data structure
    YELLOW = (255,246,0)        ##RGB colour for cadmium yellow, represented as a tuple data structure
    BLUE = (173, 216, 230)      #RGB colour for blue, represented as a tuple data structure
    Dark_BLUE = (0, 0, 255)     #RGB colour for dark blue, represented as a tuple data structure
    Mahogany_RED = (192, 64, 0) #RGB colour for mahogany red, represented as a tuple data structure
    screen = None               #Represents the screen object in python, currently set to be none
    max_width = 600             #Represents the mazimum width of the sqaure maze that is generated
    WHITE = (255, 255, 255)     #RGB colour for white, represented as a tuple data structure
    maze_map = {}               #Gives a data structure representation of where there are walls and where there are no walls in the maze
    grid = []                   #Gives the (x, y) position of each cell in the maze
    visited = []                #This is a list which represents the position of the cells that have been visited by the randomised dfs algorithm
    stack = []
    startpos = 100             #Denotes the (x, y) position of the top left corner of the maze in the pygame window the where maze is to be rendered 

    def __init__(self,w, cell_width):
        self.w = w #denotes the width of the maze
        self.cell_width = cell_width #represents the width of each cell in the square grid

    def setup_screen(self): #sets up the main pygame window when called as a method
        pygame.init()
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.screen.fill(self.BLUE)
        pygame.display.set_caption("MAZE GAME: LABYRINTH")
    
    def generate_sq_grid(self):
        x,y = self.startpos,self.startpos #changed
        for row in range(self.w+1):                                    #Draws out the rows (1 more than the width of the cell)
            for coordinate in range(self.w):                          #This for loop allows us to list the positions of the top left of each cell
                if row != self.w:                                     #Checks whether it has reached the very end of the row (we don't want the coordinates of that end)
                    self.grid.append((x,y))                           #Coordinates of the top left of each cell are appended to the "grid" list
                    self.maze_map[(x,y)] = {"N":0,"E":0,"S":0,"W":0}  #"maze map" tells us which walls are open around each cell, and the coordinates of each cell needs to be recorded there since that is our way of referencing them
                    x = x + self.cell_width                           #This moves to the next cell to the right in the row
            x = self.startpos #changed                                #Resets the x-coordinate to the starting coordinate position
            pygame.draw.line(self.screen, self.BLACK, [x, y], [x + self.max_width, y]) #Draws the line for the row, given the current value of y and the constant value of x. The line will be "self.max_width" long
            y = y + self.cell_width                                                    #Moves to the starting coordinates of the next row below
        x,y = self.startpos, self.startpos #changed                                    #After all the rows have been made, the value of x and y resets to the initial start position
        for column in range(self.w+1):                                                 #This for loop is to draw out the columns
            pygame.draw.line(self.screen, self.BLACK, [x, y], [x, y + self.max_width]) #Draws a straight, vertical line downwards
            x = x + self.cell_width

    def draw_button(self, x: int, y: int, width: int, height: int, button_font_size: int, button_text: str): #draws a button on the (x, y) position of the pygame window
        outline_size = 7  #This will be the pixel size of the yellow outline
        #These 2 lines below draw the rectangle which will be rendered on top of to form the yellow outline
        overlapping_rect = pygame.Rect(x - outline_size, y - outline_size, width + (outline_size*2), height + (outline_size*2))
        pygame.draw.rect(self.screen, self.YELLOW, overlapping_rect)

        font = pygame.font.Font('freesansbold.ttf', button_font_size) #This constructs a font object with a specific font type and font size
        #The 2 lines below will draw the rectangle for the main button
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, self.GREEN, button_rect)

        #The 2 lines of code below use the render() method to turn the button_text into image data that we then render onto the window
        button_text_display = font.render(button_text, True, self.WHITE)
        self.screen.blit(button_text_display, (x + 10, y + 10)) #The text is rendered 10 pixels right and 10 pixels down from the pixel position of the box
        return button_rect #returns a tuple that details the width, height and position of the button, which can be used later on
    
    def make_title(self, x: int, y: int, text: str, font_size: int, colour: tuple, heading_depth: int):
        #The 2 lines below draw a rectangle that is the width of the pygame screen in order to make the heading outline
        Heading = (0, 0, 1300, heading_depth) #heading_depth is just a value which depicts how low the heading outline goes 
        pygame.draw.rect(self.screen, self.Dark_BLUE, Heading)
        font = pygame.font.SysFont('impact', font_size) #This constructs a font object with a font type and font size
        #the following 3 lines below are responsible for rendering the title text onto the x,y position of the window
        heading_text_display = font.render(text, True, colour)
        self.screen.blit(heading_text_display, (x, y))
        pygame.display.update() #pygame updates to show new heading change

    def generate_text(self, x: int, y: int, text: str, font_size: int, colour: tuple):
        #code below involves construction of font object; will generate texts of an "impact" font style and a variable font size
        font = pygame.font.SysFont('impact', font_size)
        text_display = font.render(text, True, colour) #Renders the text so that it can be presented in the window
        self.screen.blit(text_display, (x, y)) #Places the text onto the pygame window
        pygame.display.update() #Updates pygame window so user can see the changes
    
    def push_up(self, x, y):
        pygame.draw.rect(self.screen, self.WHITE, (x + 1, y - self.cell_width + 1, self.cell_width-1, (2*(self.cell_width))-1), 0)  # draw a rectangle twice the width of the cell

    def push_down(self, x, y):
        pygame.draw.rect(self.screen, self.WHITE, (x +  1, y + 1, self.cell_width-1, (2*(self.cell_width))-1), 0)

    def push_left(self, x, y):
        pygame.draw.rect(self.screen, self.WHITE, (x - self.cell_width +1, y +1, (2*(self.cell_width))-1, self.cell_width-1), 0)

    def push_right(self, x, y):
        pygame.draw.rect(self.screen, self.WHITE, (x +1, y +1, (2*(self.cell_width))-1, self.cell_width-1), 0)

    def carve_out_maze(self):
        x = self.startpos
        y = self.startpos
        self.stack = []
        self.visited = []
        self.stack.append((x,y))                                            
        self.visited.append((x,y))   

        while len(self.stack) > 0:                                          
            cell = []                                                       
            if (x + self.cell_width, y) not in self.visited and (x + self.cell_width, y) in self.maze_map:       # right cell available?
                cell.append("right")                                   

            if (x - self.cell_width, y) not in self.visited and (x - self.cell_width, y) in self.maze_map:       # left cell available?
                cell.append("left")

            if (x , y + self.cell_width) not in self.visited and (x , y + self.cell_width) in self.maze_map:     # down cell available?
                cell.append("down")

            if (x, y - self.cell_width) not in self.visited and (x , y - self.cell_width) in self.maze_map:      # up cell available?
                cell.append("up")

            if len(cell) > 0:
                                           
                cell_chosen = (random.choice(cell))         #Choosing a cell at random               

                if cell_chosen == "right":                  #If the cell that is to the right of the current cell is chosen...
                    self.push_right(x, y)                   #Collapse the wall between the current cell and the chosen cell that is to the right                    
                    self.maze_map[(x,y)]["E"] = 1           #Stores the information of a collapsed wall to the right of current cell (stored in a dictionary)               
                    self.maze_map[(x + self.cell_width, y)]["W"] = 1 #Stores the information of a collapsed wall to the left of the randomly selected cell (stored in a dictionary)
                    x = x + self.cell_width                          #Used as a form of "Updating" to the new current cell                                          
                    self.visited.append((x, y))             #Marks the new cell as visited                           
                    self.stack.append((x, y))               #Pushes new cell onto stack

                elif cell_chosen == "left":                 #If the cell that is to the left of the current cell is chosen...
                    self.push_left(x, y)                    #Collapse the wall between the current cell and the chosen cell that is to the left
                    self.maze_map[(x,y)]["W"] = 1           #Stores the information of a collapsed wall to the left of current cell (stored in a dictionary)
                    self.maze_map[(x - self.cell_width, y)]["E"] = 1 #Stores the information of a collapsed wall to the right of the randomly selected cell (stored in a dictionary)
                    x = x - self.cell_width                          #Used as a form of "Updating" to the new current cell
                    self.visited.append((x, y))             #Marks the new cell as visited
                    self.stack.append((x, y))               #Pushes new cell onto stack

                elif cell_chosen == "down":                 #If the cell that is below the current cell is chosen...
                    self.push_down(x, y)                    #Collapse the wall between the current cell and the chosen cell that is below
                    self.maze_map[(x,y)]["S"] = 1           #Stores the information of a collapsed wall below the current cell (stored in a dictionary)
                    self.maze_map[(x, y + self.cell_width)]["N"] = 1 #Stores the information of a collapsed wall above the randomly selected cell (stored in a dictionary)
                    y = y + self.cell_width                          #Updates the current cell to a new cell
                    self.visited.append((x, y))             #Appends it to the list of visited nodes
                    self.stack.append((x, y))               #Appends it to the stack for future backtracking

                elif cell_chosen == "up":                   #If the cell that is above the current cell is chosen...
                    self.push_up(x, y)                      #Collapse the wall between the current cell and the chosen cell that is above
                    self.maze_map[(x,y)]["N"] = 1           #Stores the information of a collapsed wall above the current cell (stored in a dictionary
                    self.maze_map[(x, y - self.cell_width)]["S"] = 1 #Stores the information of a collapsed wall below the randomly selected cell (stored in a dictionary)
                    y = y - self.cell_width                          #Updates the current cell to a new cell
                    self.visited.append((x, y))             #Appends it to the list of visited nodes
                    self.stack.append((x, y))               #Appends it to the stack for future backtracking
            else:
                x, y = self.stack.pop()                                    
    
class maze_object(maze):

    def __init__(self, w, cell_width):
        super().__init__(w,cell_width)
        self.objwidth = self.cell_width - 6                 #Width of object
        self.objheight = self.cell_width - 6                #Height of object
        self.timer_font = pygame.font.Font(None, 36)        #font for the timer
        self.start_time = time.time()                       #stores starting time of stopwatch timer

    def update_timer(self):                       #updates the timer in the pygame window every time it is called
        time_diff = time.time() - self.start_time #Subtracts the current time by the initially recorded time (the resulting variable is a float type in seconds)
        minutes = str(int(time_diff//60))         #Calculates the number of minutes given the time difference
        seconds = str(int(time_diff%60))          #Calculates the number of seconds given the time difference
        cover_up_rect = (920, 120, 140, 70)       #Erases or "covers up" the previous timer value from the pygame windoe
        pygame.draw.rect(self.screen, self.BLUE, cover_up_rect) 

        #the following if statements make it so that the timer is like "00:00" instead of "0:0"
        if len(minutes) == 1:
            minutes = "0" + str(minutes)

        if len(seconds) == 1:
            seconds = "0" + str(seconds)
        
        new_time = f"{minutes}:{seconds}"        #This variable contains the newly obtained time as a string in minutes and seconds
        self.generate_text(920, 120, new_time, 60, self.WHITE) #Renders the newly updated time onto the pygame window
        return new_time                                        #Returns the newly calculated time as a string

    def get_rightside(self, objx, objy):
        rightside_t = []                                    #This is the data sturcture which stores the colours of the pixels; vurrently a list
        for i in range(self.objwidth):                      #Iterates through every pixel surrounding the maze object's width on a specific side 
            rightside_t.append(self.screen.get_at([int(objx + self.objwidth ), int(objy + i)])) #Adds the colour of a specific pixel on the given side
        rightside_t = tuple(rightside_t)                    #After for loop is finished, the data structure is converted into tuple again
        return rightside_t                                  #Returns the tuple consisting of all the colours of the pixels

    def get_leftside(self, objx, objy):
        leftside_t = []
        for i in range(self.objwidth):
            leftside_t.append(self.screen.get_at([int(objx - 1), int(objy + i)]))
        leftside_t = tuple(leftside_t)
        return leftside_t

    def get_upperside(self, objx, objy):
        upperside_t = []
        for i in range(self.objwidth):
            upperside_t.append(self.screen.get_at([int(objx + i), int(objy - 1)]))
        upperside_t = tuple(upperside_t)
        return upperside_t

    def get_lowerside(self, objx, objy):
        lowerside_t = []
        for i in range(self.objwidth):
            lowerside_t.append(self.screen.get_at([int(objx + i), int(objy + self.objwidth)]))
        lowerside_t = tuple(lowerside_t)
        return lowerside_t
        
    def make_object(self):

        ending_objx,ending_objy = self.startpos + 1 ,self.startpos + 1    #changed
        vel = 1
        objx,objy = self.startpos + self.max_width - (self.objheight),self.startpos + self.max_width - (self.objheight) #changed
        running_time = ""
        
        leftmost_bound = self.startpos + 1 
        rightmost_bound = (self.max_width + self.startpos) - self.objwidth
        upper_bound = self.startpos + 1 
        lower_bound = (self.max_width + self.startpos) - self.objheight 

        #the following if statements vary the slowing of the maze object depending on the maze_width input 
        if self.w == 10:
            lag = 0
        elif self.w == 20:
            lag = 1
        elif self.w == 30:
            lag = 3
        elif self.w == 40:
            lag = 3
        elif self.w == 50:
            lag = 4

        self.make_title(480, 10, "START SOLVING!", 65, self.WHITE, 90)        #Generates the title that infoms the user to start solving the maze

        #the followwing methods below draw out the buttons onto the pygame window screen...
        BFS_button = self.draw_button(850, 250, 300, 70, 40, "BFS Algorithm")
            
        DFS_button = self.draw_button(850, 380, 300, 70, 40, "DFS Algorithm")

        Astar_button = self.draw_button(850, 510, 300, 70, 40, "A* Algorithm")

        Back_button = self.draw_button(1130, 700, 140, 70, 50, "Back")     

        while True :                              #While program is still running...
            pygame.time.delay(lag)               #Slows down maze object movement

            for event in pygame.event.get():
                if event.type == pygame.QUIT: #Checks if user has closed window
                    quit()

                #the following if statements and nested if statements check if the user has clicked on a button
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos() #returns pygame window position of mouse cursor click

                    if BFS_button.collidepoint(mouse_x, mouse_y): #Checks if the mouse click is within the "BFS Algorithm" button
                        return "BFS", running_time                #Returns the name of the button selected and the time the user was playing for

                    if DFS_button.collidepoint(mouse_x, mouse_y): #Checks if the mouse click is within the "DFS Algorithm" button
                        return "DFS", running_time                #Returns the name of the button selected and the time the user was playing for

                    if Astar_button.collidepoint(mouse_x, mouse_y): #Checks if the mouse click is within the "A* Algorithm" button
                        return "A*", running_time                   #Returns the name of the button selected and the time the user was playing for
                    
                    if Back_button.collidepoint(mouse_x, mouse_y):  #Checks if the mouse click is within the "Back" button
                        return "Back", running_time                 #Returns the name of the button selected and the time the user was playing for 
                    
            running_time = self.update_timer() #this method updates the timer in the window

            if objx == ending_objx and objy == ending_objy: #Checks if the maze object reaches the top left of the maze (the goal)
                return "Solved", running_time               #Returns "Solved" and the time the user was playing for
                                    
            keys = pygame.key.get_pressed()   #Method which assigns any potential key presses made to the "key" variable
            tempobjx = objx                   #Stores x coordinates of maze object before any changes
            tempobjy = objy                   #Stores y coordinates of maze object before any changes

            RightSide = self.get_rightside(objx,objy) #Returns a tuple of all of the colours surrounding the right side of the maze object
            LeftSide =  self.get_leftside(objx,objy)  #Returns a tuple of all of the colours surrounding the left side of the maze object
            UpperSide = self.get_upperside(objx,objy) #Returns a tuple of all of the colours surrounding the upper side of the maze object
            LowerSide = self.get_lowerside(objx,objy) #Returns a tuple of all of the colours surrounding the lower side of the maze object

            if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and objx > leftmost_bound and self.BLACK not in LeftSide:   #if the left or 'A' key is pressed...
                objx -= vel                   #Move 1 (pixel) coordinate leftwards

            if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and objx  < rightmost_bound and self.BLACK not in RightSide:  #if the right or 'D' key is pressed...
                objx += vel                   #Move 1 (pixel) coordinate rightwards 

            if (keys[pygame.K_UP] or  keys[pygame.K_w]) and objy > upper_bound and self.BLACK not in UpperSide:    #if the upwards or 'W' key is pressed...
                objy -= vel                                 #Move 1 (pixel) coordinate upwards

            if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and objy < lower_bound and self.BLACK not in LowerSide:   #if the downwards or 'S' key is pressed...
                objy += vel                                 #Move 1 (pixel) coordinate downwards
            
            pygame.draw.rect(self.screen, self.WHITE , (tempobjx, tempobjy, self.objwidth, self.objheight))  # The method that creates a green trail made by moving the maze object
            pygame.draw.rect(self.screen, self.Dark_BLUE, (ending_objx, ending_objy, self.objwidth, self.objheight))
            pygame.draw.rect(self.screen, self.RED , (objx, objy, self.objwidth, self.objheight))            #Draws position of new rectangle

            pygame.display.update()

class Searching_algos(maze_object):
    def __init__(self, w, cell_width):
        super().__init__(w,cell_width)                                    #inherits from the superclass "maze_object"
        self.start_cell = ((self.max_width + self.startpos) - self.cell_width, (self.max_width + self.startpos) - self.cell_width)  #Starting cell coordinates
        self.goal_cell = (self.startpos, self.startpos)                   #This is the goal cell (top leftmost cell)

    def next_cell(self, dir, Cell): #This is the function which returns the position of a neighbouring cell from a current cell in a specific direction
        if dir =='E':  #if we want to find the (x, y) position of the cell that is to the right (East) of our current cell...
            nextcell = (Cell[0] + self.cell_width, Cell[1]) #we add the current cell's x value by the cell width to get the position
        elif dir == 'S':  #if we want to find the (x, y) position of the cell that is below (south of) the current cell...
            nextcell = (Cell[0], Cell[1] + self.cell_width) #we add the current cell's y value by the cell width to get the position
        elif dir =='N': #if we want to find the (x, y) position of the cell that above (north of) our current cell...
            nextcell = (Cell[0], Cell[1] - self.cell_width) #We subtract the y-value of the current cell by the cell width to get the required position
        elif dir == 'W': #if we want to find the (x, y) position of the cell that is to the left (west) of our current cell...
            nextcell = (Cell[0] - self.cell_width, Cell[1]) #we subtract the current cell's x value by the cell width to get the position
        return nextcell #returns the postion of the neighbouring cell
    
    def solution_map(self, path):  #Obtains the solution path given the aPath dictionary from any of the 3 algorithms
        SolutionPath = {}               #this is the dictionary which will contain the path for the solution
        cell = self.goal_cell      
        while cell != self.start_cell: #While we haven't reached the start cell...
            SolutionPath[path[cell]] = cell #swap the value and the key so the path will be going the other way
            cell = path[cell]          #This allows for the program to move to the next cell in the path from
        return SolutionPath            #Returns the solution path as a dictionary

    def h(self, cell1): #returns the manhattan distance between a selected cell and the starting cell
        x1, y1 = self.goal_cell         # x and y values of the goal cell (which is always constant)
        x2, y2 = cell1         # x and y values of the second cell
        return abs(x1 - x2) + abs(y1 - y2) #Returns the manhattan distance (which will be our heuristic)
    
    def tracepath(self,path):           #traces out the solution path
        ncell = path[self.start_cell]   #Initially the methods starts by rendering the start cell
        run = True                      #This boolean variable tells us whether the 

        starting_x_coordinate = self.start_cell[0] + ((self.cell_width//2) - (self.cell_width//10))  #x coordinate of the square
        starting_y_coordinate = self.start_cell[1] + ((self.cell_width//2) - (self.cell_width//10))  #y coordinate of the square
        square_width = self.cell_width//5

        pygame.draw.rect(self.screen, self.RED , (starting_x_coordinate, starting_y_coordinate ,square_width, square_width)) #draws out the square of the starting cell

        while run:   #while there are still cells to be rendered...
            for event in pygame.event.get():
                    if event.type == pygame.QUIT: #Checks if user has closed window
                        run = False               #if user has closed the window, thepygame 
                        pygame.quit()
                        quit()
            
            if ncell != self.goal_cell:    #if the current cell retrieved from the solution path dictionary is not the goal cell...
                ncell_x_coordinate = ncell[0] + ((self.cell_width//2) - (self.cell_width//10)) #x coordinate of the smaller square in cell
                ncell_y_coordinate = ncell[1] + ((self.cell_width//2) - (self.cell_width//10)) #y coordinate of the smaller square in cell
                pygame.draw.rect(self.screen, self.RED , (ncell_x_coordinate , ncell_y_coordinate, square_width, square_width)) #Draws a square of a cell that makes up the path
                pygame.display.update() #updates the display
                time.sleep(0.025)       #Allows for time between rendering of each small square to be slowed down for pathfinding visualisation
                ncell = path[ncell]     #lets the next cell in the solution path equal to ncell variable
            else:
                run = False             #This is when the current cell IS the goal cell; the while loop ends as a result since all the cells are rendered
        
        starting_x_coordinate = self.goal_cell[0] + ((self.cell_width//2) - (self.cell_width//10))  #x coordinate of the square
        starting_y_coordinate = self.goal_cell[1] + ((self.cell_width//2) - (self.cell_width//10))  #y coordinate of the square
        square_width = self.cell_width//5

        pygame.draw.rect(self.screen, self.Dark_BLUE , (starting_x_coordinate, starting_y_coordinate ,square_width, square_width)) #draws out the square of the ending cell
        pygame.display.update()


    def Astar_algo(self): #returns the solution path for the maze using the A* algorithm
        g_score = {cell:float("inf") for cell in self.grid}  #initiates a dictionary which consists of the path cost of all the cells
        g_score[self.start_cell] = 0                         #sets the path cost of the start cell to be 0
        f_score = {cell:float("inf") for cell in self.grid}  #initiates a dictionary which consists of the f_score of all of the cells
        f_score[self.start_cell] = self.h(self.start_cell) #sets f cost of the starting cell, which is just heuristic cost

        cell_queue = PriorityQueue()       #declares the priority queue, and the code below places the starting cell in the queue, along with its f and h score
        cell_queue.put((self.h(self.start_cell), self.h(self.start_cell), self.start_cell))
        aPath = {}   #declares the path dictionary for further use

        while not cell_queue.empty():
            currCell = cell_queue.get()[2] #Retrieves the value with the lowest f cost

            if currCell== self.goal_cell: #if the cell that we are in is the goal cell, then we have finished and the program exits the loop
                break
        
            for direction in 'ESNW':    #looks through every side of the cell we are currently in (East, North, South and West side)
                if self.maze_map[currCell][direction] == 1:  #if this side of the cell has no wall, then we can examine and analyse the cell that is in that direction
                    childcell = self.next_cell(direction, currCell)       #returns the position of the neighbouring cell in a direction
                    
                    square_width = self.cell_width//5
                    childcell_x_coordinate = childcell[0] + ((self.cell_width//2) - (self.cell_width//10)) #x coordinate of the smaller square in cell
                    childcell_y_coordinate = childcell[1] + ((self.cell_width//2) - (self.cell_width//10)) #y coordinate of the smaller square in cell
                    pygame.draw.rect(self.screen, self.BLACK , (childcell_x_coordinate , childcell_y_coordinate, square_width, square_width)) #Draws a square of a cell that makes up the path
                    pygame.display.update() #Updates pygame window to show the newly examined cell
                    time.sleep(0.005)       #Time lag allows for the rendering to slow down for the user to see

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: #Checks if user has closed window
                            pygame.quit()
                            quit()
                    
                    temp_g_score = g_score[currCell] + self.cell_width    #finds path cost of childcell that could replace the current gscore of the child cell
                    temp_f_score = temp_g_score + self.h(childcell)   #sum of calculated path cost and the heuristic cost t0 find f cost       

                    if temp_f_score < f_score[childcell]:     #if the new f cost is less than the old f cost of the child cell...
                        g_score[childcell] = temp_g_score     #replace the old previous path cost with the new path  and lower cost
                        f_score[childcell] = temp_f_score     #replace the old f cost of the child cell with the new cost
                        cell_queue.put((temp_f_score,self.h(childcell), childcell)) #add child cell and the g cost and the f cost to priority queue
                        aPath[childcell] = currCell    #set the previous path of the child cell to be the current cell in the path dictionary
        
        fwdPath = self.solution_map(aPath) #Returns the solution path given the current path
        return fwdPath                     #Since Astar_algo is essentially a function, it returns a dictionary of the solution path, which we can then use for rendering

    def BFS_algo(self):
        cell_queue = [self.start_cell] #this is the queue for all of the cells to be fully visited
        visited = [self.start_cell]    #list of cells that have been visited/encountered
        bpath = {}                     #this is the path of the connections between cells

        while len(cell_queue) > 0:         #while there are still cells to be fully visited...
            currCell = cell_queue.pop(0)   #pop first item from the queue
            if currCell == self.goal_cell: #if the cell we're currently in is the goal cell...
                break #end the loop and the algorithm ends too
    
            for d in "ESNW":                                #For every direction around the current cell...
                if self.maze_map[currCell][d] == 1:         #If there is no wall between current cell and a neighbouring cell in a specific direction...

                    childcell = self.next_cell(d, currCell) #Derive its position using the next_cell() method we formed before
                    square_width = self.cell_width//5
                    childcell_x_coordinate = childcell[0] + ((self.cell_width//2) - (self.cell_width//10)) #x coordinate of the smaller square in cell
                    childcell_y_coordinate = childcell[1] + ((self.cell_width//2) - (self.cell_width//10)) #y coordinate of the smaller square in cell
                    pygame.draw.rect(self.screen, self.BLACK , (childcell_x_coordinate , childcell_y_coordinate, square_width, square_width)) #Draws a square of a cell that makes up the path
                    pygame.display.update()
                    time.sleep(0.005)

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: #Checks if user has closed window
                            pygame.quit()
                            quit()
                        

                    if childcell not in visited:            #if the current cell has not been visited...
                        cell_queue.append(childcell)        #Append it to the queue of cells that are yet to be fully visited
                        visited.append(childcell)           #Append it to the list of visited cells
                        bpath[childcell] = currCell         #Record which cell the childcell was previously connected to (which will be the current cell)
        
        fwdPath = self.solution_map(bpath)   #make a dictionary which denotes the solution path
        return fwdPath 

    def DFS_algo(self):
        visited = [self.start_cell]          #list of cells that have been visited/encountered
        DFSstack = [self.start_cell]         #This stack is used to backtrack to previous cells
        dpath = {}                           #This shows the connection between the cells

        while len(DFSstack) > 0:             #while the stack is not empty...
            currCell = DFSstack.pop()        #Pop a cell from the stack
            if currCell == self.goal_cell:   #if the current cell is the goal cell, break from the algorithm
                break

            for d in 'ESNW':                                #For every direction around the current cell...
                if self.maze_map[currCell][d] == 1:         #If there is no wall between current cell and a neighbouring cell in a specific direction...
                    childcell = self.next_cell(d, currCell) #Derive its position using the next_cell() method we formed before
                    square_width = self.cell_width//5
                    childcell_x_coordinate = childcell[0] + ((self.cell_width//2) - (self.cell_width//10)) #x coordinate of the smaller square in cell
                    childcell_y_coordinate = childcell[1] + ((self.cell_width//2) - (self.cell_width//10)) #y coordinate of the smaller square in cell
                    pygame.draw.rect(self.screen, self.BLACK , (childcell_x_coordinate , childcell_y_coordinate, square_width, square_width)) #Draws a square of a cell
                    pygame.display.update() #updates pygame window
                    time.sleep(0.005)       #Lag is used to slow program down to enable the user to better visualise the path.
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT: #Checks if user has closed window
                            pygame.quit()
                            quit()
                    
                    if childcell not in visited:     #if the current cell has not been visited...
                        visited.append(childcell)    #Append it to the list of visited cells
                        DFSstack.append(childcell)   #Push it onto the stack
                        dpath[childcell] = currCell  #Record which cell the childcell was previously connected to (which will be the current cell)
        
        fwdPath = self.solution_map(dpath) #make a dictionary which denotes the solution path
        return fwdPath                     #Return it for further rendering

class UserInterface(Searching_algos):
   def __init__(self):
        self.database_path = "C:\\Users\\Sulav\\Desktop\\My_Projects\\NEA\\NEA_Main\\user_data.db"
        self.user_data = {"name": " ", "password": " ", "10": None, "20": None, "30": None, "40": None, "50": None}      
        self.starting_screen() #the starting/login screen is the first to be initialised
       
   def starting_screen(self):
       self.setup_screen() #This sets up the pygame window for which the rendering will occur
       self.make_title(280, 23, "WELCOME TO: LABYRINTH!!!", 70, self.WHITE, 120) #Generates a heading for the window, welcoming the user
       
       login_button = self.draw_button(560, 250, 216, 90, 64, "Log in")   #Draws a button onto the pygame window titled "Login"
       sign_in_button = self.draw_button(550, 400, 240, 90, 64, "Sign in")#Draws a button onto the pygame window titled "Sign in"
       rules_button = self.draw_button(565, 550, 200, 90, 64, "Rules")    #Draws a button onto the pygame window titled "Rules"
       
       pygame.display.update()

       while True: #The while loop will continue to run indefinitely until one of the buttons are clicked or the window is closed
           
           for event in pygame.event.get(): #checks for any user input
               if event.type == pygame.QUIT: #If the user chooses to close the window...
                   pygame.quit() #Pygame is closed
                   quit() #Programme is terminated with no error, so window closes
                
               elif event.type == pygame.MOUSEBUTTONDOWN: #Checks for any cursor clicks within the pygamw window
                   mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the position of the cursor click

                   if login_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the "Play" button...
                       self.login_screen() #Go to inputs window

                   elif rules_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the "Rules" button...
                       self.rules_screen() #Go to the rules window

                   elif sign_in_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the "Quit" button...
                       self.sign_in_screen()
   
   def username_exists(self, username):
        conn = sqlite3.connect(self.database_path) #forms a connection between the database and the program
        cursor = conn.cursor()                     #cursor is formed to execute and save the results from queries
        queary = """SELECT username FROM users WHERE username = ?"""  #formation of a query
        cursor.execute(queary, (username,))        #executes the queries and fills out the missing "?" spaces by using the values in the tuples
        result = cursor.fetchone()                 #the result is returned using the fetchone() method
        conn.close()                               #closes the database connection and ends the transaction

        #the code below checks the result to see if the username exists
        if result is not None:                     
            return True       #returns true if it exists
        else:
            return False      #returns false if username doesn't exist
    
   def account_exists(self, username, password):    
        conn = sqlite3.connect(self.database_path)  #forms a connection between the database and the program
        cursor = conn.cursor()                      #cursor is formed to execute and save queries
        queary = """SELECT username FROM users WHERE username = ? AND password = ?""" #formation of a query
        cursor.execute(queary, (username, password))#executes the queries and fills out the missing spaces by using the values in the tuples
        result = cursor.fetchone()                  #the result is returned using the fetchone() method
        conn.close()                                #closes the database connection and ends the transaction
        
        #the code below checks the result to see if the account exists
        if result is not None:
            return True        #returns true if it exists
        else:
            return False       #returns false if account doesn't exist

#If the value of result is anything other than "None", then it's the username, so True is returned to show that the account exists since the username exists
    
   def add_user(self, username, password):
        conn = sqlite3.connect(self.database_path) #forms a connection between the database and the program
        cursor = conn.cursor()                     #cursor is formed to execute and save queries

        queary = '''INSERT INTO users (username, password) VALUES (?, ?)''' #formation of a query
        cursor.execute(queary, (username, password)) #executes the queries and fills out the missing spaces by using the values in the tuples

        conn.commit() #changes to the database has to be committed in order to make them permanent
        conn.close()  #closes the database connection and ends the transaction

        return {"name":username, "password":password, "10": None, "20": None, "30": None, "40": None, "50": None} #returns a dictionary of all the attributes and their values
   
   def get_details(self, username, password):
        conn = sqlite3.connect(self.database_path)    #forms a connection between the database and the program
        cursor = conn.cursor()                        #cursor is formed to execute and save queries
        query = """SELECT * FROM users WHERE username = ? AND password = ?""" #forms the query
        cursor.execute(query, (username, password)) #executes the queries and fills out the missing spaces by using the values in the tuples
        record = cursor.fetchone() #returns the result of the record gathered from the executed query
        conn.close()               #closes the connection to the database to close the transaction
        #the instruction below returns a dictionary of the user data, with the key being a "field" of that record and the value being the data stored
        return {"name":record[0], "password":record[1], "10": record[2], "20": record[3], "30": record[4], "40": record[5], "50": record[6]}

   def change_time(self, maze_size, time):
        conn = sqlite3.connect(self.database_path)    #forms a connection between the database and the program
        username = self.user_data["name"]             #finds the username for later use
        cursor = conn.cursor()                        #cursor is formed to execute and save queries
        maze_sizes = ('X_MAZE_TIME','XX_MAZE_TIME','XXX_MAZE_TIME' ,'XL_MAZE_TIME' , 'L_MAZE_TIME') #this is the names of the columns of the database as a tuple
        column_name = maze_sizes[(int(maze_size)//10)-1]  #returns the name of the attribute which we will change the time for, using the tuple above as well as the maze_size value
        query = f'''UPDATE users SET {column_name} = ? WHERE username = ?''' #forms the query that will change the user's best time for a maze size in the users database, given their username
        cursor.execute(query, (time, username))       #executes the queries and fills out the missing spaces by using the values in the tuples
        conn.commit()                                 #Makes sure that the changes are saved by comitting them
        conn.close()                                  #closes the connection to the database to close the transaction

   def login_screen(self):
       self.screen.fill(self.BLUE) #Erases previous window
       back_button = self.draw_button(1130, 700, 140, 70, 50, "Back") #Draws "back" button onto pygame window and returns its position, height and width
       self.make_title(50, 23, "LOG INTO ACCOUNT (Press enter to submit)", 70, self.WHITE, 120) #Generates a heading for the window
       
       #the two lines of code render the words "Username" and "Password" above the text boxes
       self.generate_text( 100, 190, "Username:", 45, self.WHITE) 
       self.generate_text( 100, 320, "Password:", 45, self.WHITE)
       
       #the 4 lines of code represent and draw the text boxes where the user will type into
       username_text_box_rect = pygame.Rect(100, 250, 400, 50)
       password_text_box_rect = pygame.Rect(100, 380, 400, 50)
       pygame.draw.rect(self.screen,self.WHITE , username_text_box_rect)
       pygame.draw.rect(self.screen,self.WHITE , password_text_box_rect)

       font = pygame.font.Font("freesansbold.ttf", 32) #This represents the font type and size of the text we will be rendering

       Username = "" #This is where the username input will be stored when the user types into the text box
       Password = "" #This is where the password input will be stored when the user types into the text box
       
       username_input = True
       password_input = False

       pygame.display.update() #updates the pygame window to show the changes

       while True: #The while loop rund indefinitely until the user either closes the window or clicks a button
            for event in pygame.event.get():  #Checks for any user input
                if event.type == pygame.QUIT: #if the user wants to close the window...
                    quit()                    #programme terminates, so window closes
                
                elif event.type == pygame.KEYDOWN:      #If the user input is a keyboard input...
                    if event.key == pygame.K_BACKSPACE: #if the user presses the backspace key...
                        if username_input:              #checks if user is typing on the username text box
                            Username = Username[:-1]    #Remove last character from username string if user is typing on username text box
                        elif password_input:   #if user isn't choosing to type on username textbox, it checks if they are typing on password textbox
                            Password = Password[:-1]    #Remove last character from password string if user is typing on password text box
                    
                    elif event.key == pygame.K_RETURN: #If the user presses enter (to submit their username and password)...

                        if self.account_exists(Username, Password): #Checks if the entered username and password exist in the database
                            self.user_data = self.get_details(Username, Password) #if username and password exist, all user data is retrieved for later use
                            self.main_menu_screen() #the user is taken to post login/signin screen

                        else: #if the username or password don't exist...
                            #the 2 lines of code below inform the user that the account doesn't exist or details are entered incorrectly
                            text = "ERROR: ACCOUNT DOESN'T EXIST OR USERNAME/PASSWORD ENTERED INCORRECTLY"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)

                    else: #This is the condition for any other key presses than the return and backspace key
                        if username_input:             #Checks if the user is typing on the username text box 
                            Username += event.unicode  # Adds the inputted character to the username string
                        if password_input:             #Checks if the user is typing on the password text box
                            Password += event.unicode  # Adds the inputted character to the password string
  
                elif event.type == pygame.MOUSEBUTTONDOWN:    #Checks for any mouse/cursor clicks
                    mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the pygame window position of any cursor clicks

                    if back_button.collidepoint(mouse_x, mouse_y): #If the position of the mouse click is inside the back button...
                        self.starting_screen()                     #User is taken back to the starting window

                    elif username_text_box_rect.collidepoint(mouse_x, mouse_y): #Checks if the position of the mouse click is inside the username text box
                        #The following 2 lines are written so user's inputted text will only show up on the username textbox, not on both of the text boxes
                        username_input = True 
                        password_input = False
                        
                    elif password_text_box_rect.collidepoint(mouse_x, mouse_y): #Checks if the position of the mouse click is inside the password text box
                        #The following 2 lines are written so user's inputted text will only show up on the username textbox, not on both of the text boxes
                        password_input = True
                        username_input = False
            
            #The following lines of code below render the contents of the username/password string variables onto the text boxes to show potential key presses/deletions onto the screen
            pygame.draw.rect(self.screen,self.WHITE , username_text_box_rect)
            rendered_text = font.render(Username, True, self.BLACK)
            self.screen.blit(rendered_text, (105, 255))
            pygame.display.update()

            pygame.draw.rect(self.screen,self.WHITE , password_text_box_rect)
            rendered_text = font.render(Password, True, self.BLACK)
            self.screen.blit(rendered_text, (105, 385))
            pygame.display.update() 

   def sign_in_screen(self):
        self.screen.fill(self.BLUE)
        back_button = self.draw_button(1130, 700, 140, 70, 50, "Back") #Draws "back" button onto pygame window and returns its position, height and width
        self.make_title(50, 23, "MAKE AN ACCOUNT (Press enter to submit)", 70, self.WHITE, 120) #Generates a heading for the window
        
        #the two lines of code render the words "Username" and "Password" above the text boxes
        self.generate_text( 100, 190, "Make a Username:", 45, self.WHITE)
        self.generate_text( 100, 320, "Make a Password:", 45, self.WHITE)

        #the 4 lines of code represent and draw the text boxes where the user will type into
        username_text_box_rect = pygame.Rect(100, 250, 400, 50)
        password_text_box_rect = pygame.Rect(100, 380, 400, 50)
        pygame.draw.rect(self.screen,self.WHITE , username_text_box_rect)
        pygame.draw.rect(self.screen,self.WHITE , password_text_box_rect)


        font = pygame.font.Font("freesansbold.ttf", 32)

        Username = ""
        Password = ""
        username_input = True
        password_input = False

        pygame.display.update()

        while True:     #runs until user decides to close window or they go to another screen
            for event in pygame.event.get(): #looks for any user input
                if event.type == pygame.QUIT: #if user closes window...
                    quit() #program terminates and pygame window closes
                
                elif event.type == pygame.KEYDOWN:      #if a key is pressed by the user...
                    if event.key == pygame.K_BACKSPACE: #checks if the user presses the backspace key
                        if username_input:              #Used to check the user is currently using the username text box
                            Username = Username[:-1]    #Removes last character that was entered by user onto username string
                        elif password_input:            #Used to check the user is currently using the password text box
                            Password = Password[:-1]    #Removes last character that was entered by user onto password string
                    
                    elif event.key == pygame.K_RETURN:  #checks if user presses enter (to submit their username and password)

                        #the following if statements (except the final one) are used to validate whether username/password input is appropriate
                        if Username.isspace() or len(Username) == 0 or Password.isspace() or len(Password) == 0: #Checks if the username has no character input
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Username or Password has no input, please input"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)
                        
                        elif (" " in Username) == True or (" " in Password) == True:
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Username or Password inputs should have NO SPACES"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)
                        
                        elif Username[0].islower():
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Make sure the first letter of your username is in upper case"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)
                        
                        elif Password.islower():
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Password has no upper case letters, please add at least one"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)

                        elif Password.isalpha():
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Make sure your password has at least one digit"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)

                        elif len(Password) <=4:
                            erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                            pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                            text = "Make sure your password is at least 5 letters long please"
                            self.generate_text(100, 440, text, 30, self.Mahogany_RED)
                        
                        else: #this if statement checks whether the username entered already exists, after username passes all the validations
                            alr_exists = self.username_exists(Username) #this method checks if username exists within the users database, thus returning a boolean value
                            
                            if alr_exists: #if the username already exists...
                                #the 2 lines of code below erase any other error that was present in the error presenting area of the window
                                erasing_rectangle = pygame.Rect(100, 440, 1200, 35)
                                pygame.draw.rect(self.screen, self.BLUE, erasing_rectangle)
                                #these 2 lines of code below inform the user of the issue
                                text = "Username already exists, please make another one"
                                self.generate_text(100, 440, text, 30, self.Mahogany_RED)
                    
                            else: #if username hasn't been used...
                                self.user_data = self.add_user(Username, Password) #this method s=is used to add the new user into the database
                                self.main_menu_screen() #the user is directed towards the post sign in/log in window, which is the main menu

                    else: #checks for any key other than the return and backspace key
                        if username_input:             #checks if user is currently typing on the username textbox
                            Username += event.unicode  # Adds typed character to the username string
                        if password_input:             #checks if user is currently typing on the password textbox
                            Password += event.unicode  # Adds typed character to the password string
  
                elif event.type == pygame.MOUSEBUTTONDOWN:    #Checks for any mouse/cursor clicks
                    mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the pygame window position of any cursor clicks

                    if back_button.collidepoint(mouse_x, mouse_y): #If the position of the mouse click is inside the back button...
                        self.starting_screen()                     #Go to the starting screen

                    elif username_text_box_rect.collidepoint(mouse_x, mouse_y): #Checks if the position of the mouse click is inside the username text box
                        #The following 2 lines are written so user's inputted text will only show up on the username textbox, not on both of the text boxes
                        username_input = True
                        password_input = False
                        
                    elif password_text_box_rect.collidepoint(mouse_x, mouse_y): #Checks if the position of the mouse click is inside the password text box
                        #The following 2 lines are written so user's inputted text will only show up on the password textbox, not on both of the text boxes
                        password_input = True
                        username_input = False
            
            #The following lines of code below render the contents of the username/password string variables onto the text boxes to show potential key presses/deletions onto the screen
            pygame.draw.rect(self.screen,self.WHITE , username_text_box_rect)
            rendered_text = font.render(Username, True, self.BLACK)
            self.screen.blit(rendered_text, (105, 255))
            pygame.display.update()

            pygame.draw.rect(self.screen,self.WHITE , password_text_box_rect)
            rendered_text = font.render(Password, True, self.BLACK)
            self.screen.blit(rendered_text, (105, 385))
            pygame.display.update()

   def main_menu_screen(self):
        self.screen.fill(self.BLUE) #Erases previous screen
        
        self.make_title(90, 23, "THANK YOU FOR SIGNING UP/LOGGING IN", 70, self.WHITE, 120) #Generates the title of the window
        self.generate_text(400, 130, "You're now in your account", 40, self.WHITE) #Generates the text that informs the user is in their account
        self.generate_text(140, 175, "Click on this Play button which guides you to the input window", 40, self.WHITE) #Leads them to the window where they select the maze sizes
        
        play_button = self.draw_button(560, 300, 170, 90, 64, "Play")  #Draws a button onto the pygame window titled "Play"
        player_stat_button = self.draw_button(445, 450, 410, 90, 64, "Player Stats") #This is the button that leads to the player stats
        sign_out_button = self.draw_button(505, 600, 290, 90, 64, "Sign out") #This is the button that gives the option for the user to sign out

        pygame.display.update()

        while True: #The while loop will continue to run indefinitely until one of the buttons are clicked or the window is closed
           
            for event in pygame.event.get(): #checks for any user input
                if event.type == pygame.QUIT: #If the user chooses to close the window...
                    pygame.quit() #Pygame is closed
                    quit() #Programme is terminated with no error, so window closes
                
                elif event.type == pygame.MOUSEBUTTONDOWN: #Checks for any cursor clicks within the pygamw window
                    mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the position of the cursor click

                    if play_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the "Play" button...
                        self.inputs_screen() #Go to inputs window
                    
                    elif player_stat_button.collidepoint(mouse_x, mouse_y):
                        self.player_stats()
                    
                    elif sign_out_button.collidepoint(mouse_x, mouse_y): #if the user chooses to sigh out
                        self.user_data = {"name": " ", "password": " ", "10": None, "20": None, "30": None, "40": None, "50": None} #set user_data dictionary to default
                        self.starting_screen() #return to the starting screen where the user will be asked to login/sign in again

   def player_stats(self): #Make a window that shows the player's best performing time on each maze
       self.screen.fill(self.BLUE) #erases the previous screen contents
       self.make_title(50, 23, "PLAYER STATS (Your best times)", 70, self.WHITE, 120) #Generates a heading for the window
       back_button = self.draw_button(1130, 700, 140, 70, 50, "Back") #renders the back button onto the pygame screen
       dimensions = ("10","20","30","40","50") #this is a tuple which the elements are the maze sizes
       y_val = 190                             #this is the y-coordinate of the first bit of text that will be rendered to show the maze times

       for maze_width in dimensions:  #iterates through the dimensions tuple for each maze width
           min_time = self.user_data[maze_width] #uses the user_data dictionary to render the maze width
           self.generate_text(570, y_val, f"{maze_width}x{maze_width}: {min_time}", 50, self.WHITE) #generates the text showing the maze size and the user's best time as a vertical list
           y_val += 120 #y value of the next text to be rendered is added by 120 so it is rendered below the text that was just rendered

       pygame.display.update()

       while True: #The while loop will continue to run indefinitely until one of the buttons are clicked or the window is closed
           
            for event in pygame.event.get(): #checks for any user input
                if event.type == pygame.QUIT: #If the user chooses to close the window...
                    pygame.quit() #Pygame is closed
                    quit() #Programme is terminated with no error, so window closes
                
                elif event.type == pygame.MOUSEBUTTONDOWN: #Checks for any cursor clicks within the pygamw window
                    mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the position of the cursor click
                    
                    if back_button.collidepoint(mouse_x, mouse_y): #Checks if the mouse was clicked within the "back button"
                        self.main_menu_screen()                    #if true, program takes user back to main menu screen

   def rules_screen(self):
       self.screen.fill(self.BLUE) #Fills the screen with the normal blue backgrpund colour to erase the previous window
       back_button = self.draw_button(1130, 700, 140, 70, 50, "Back") #Draws "back" button onto pygame window and returns its position, height and width
       self.make_title(50, 23, "RULES: HOW TO PLAY", 70, self.WHITE, 120) #Generates the title of the window

       #The following lines of code below all call a method that renders a text onto the pygame window, allowing us to display texts
       self.generate_text(10, 130, "- The main aim of the puzzle game is to solve mazes as quick as possible", 40, self.WHITE)
       self.generate_text(10, 175, "- You start with a red maze object at the bottom right, and you move it to the top", 40, self.WHITE)
       self.generate_text(10, 220, "   left of the maze (where the blue square is); work against the timer!", 40, self.WHITE)
       self.generate_text(10, 265, "- Use the arrow keys or the WASD keys to move the maze object around", 40, self.WHITE)
       self.generate_text(10, 310, "- If you are unable to solve the maze, that's fine! Use one of the 3 algorithms that", 40, self.WHITE)
       self.generate_text(10, 355, "   will solve the maze for you (BFS, DFS or A*) and will also visualise the path", 40, self.WHITE)
       self.generate_text(10, 400, "- The solution path will be shown clearly in RED", 40, self.WHITE)
       self.generate_text(10, 445, "- Choose the maze size that is not too hard, but is challenging enough for you", 40, self.WHITE)
       self.generate_text(10, 490, "- A timer will be present at the right of the maze so you can see how much time", 40, self.WHITE)
       self.generate_text(10, 535, "   you are taking on the maze", 40, self.WHITE)
       self.generate_text(10, 580, "- The green boxes with yellow outlines are buttons for you to select", 40, self.WHITE)
       self.generate_text(10, 625, "- Advice: Start with a 10x10 maze to get used to the controls and go from there!", 40, self.WHITE)
       self.generate_text(10, 670, "- Lastly, have fun solving these maze puzzles!!!", 40, self.WHITE)
       pygame.display.update() #Updates pygame window to show the displayed changes

       while True: #The following while loop runs indefinitely until the user closes the window or a button is pressed
           
           for event in pygame.event.get(): #Checks for amy user input
               if event.type == pygame.QUIT: #If the user input is to close the window...
                   pygame.quit() #Pygame is quit and the program is terminated
                   quit()
               elif event.type == pygame.MOUSEBUTTONDOWN: #Vhecks for any mouse/cursor clicks
                   mouse_x, mouse_y = pygame.mouse.get_pos() #Returns the pygame window position of any cursor clicks

                   if back_button.collidepoint(mouse_x, mouse_y): #If the position of the mouse click is inside the back button...
                       self.starting_screen() #Go to the menu screen


   def inputs_screen(self):
       self.screen.fill(self.BLUE) #Erases the contents of the previous screen
       #The following methods before the while loop draw a button onto the pygame screen and return its rectangular properties (x, y, width, height)
       back_button = self.draw_button(1130, 700, 140, 70, 50, "Back")

       X_button = self.draw_button(570, 190, 225, 80, 64, "10x10")

       XX_button = self.draw_button(570, 310, 225, 80, 64, "20x20")

       XXX_button = self.draw_button(570, 430, 225, 80, 64, "30x30")

       XL_button = self.draw_button(570, 550, 225, 80, 64, "40x40")

       L_button = self.draw_button(570, 670, 225, 80, 64, "50x50")

       #pygame window is updated to display these buttons
       pygame.display.update()

       while True: #the while loop indefinitely displays this window until the user clicks a button and moves to another window or until they close the window
           
           self.make_title(385, 23, "SELECT A MAZE SIZE", 70, self.WHITE, 120) #This method allows for us to generate a heading title with ease

           #The following for loop detects whether the window has been closed or whether a button has been clicked
           for event in pygame.event.get():  #Looks for any events such as keyboard clicks/mouse clicks within the pygame window
               if event.type == pygame.QUIT: #This statement closes the program (and thus the window) if the "close window" icon is clicked
                   pygame.quit()
                   quit()
               
               elif event.type == pygame.MOUSEBUTTONDOWN:     #This detects any mouse clicks/cursor clicks
                   mouse_x, mouse_y = pygame.mouse.get_pos()  #This returns the x, y position of the mouse click on the pygame window

                   if X_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the 10x10 maze button...
                       self.play_screen(10) #The program will go to the maze game window with the 10x10 maze

                   if XX_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the 20x20 maze button...
                       self.play_screen(20) #The program will go to the maze game window with the 20x20 maze

                   if XXX_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the 30x30 maze button...
                       self.play_screen(30) #The program will go to the maze game window with the 30x30 maze

                   if XL_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the 40x40 maze button...
                       self.play_screen(40) #The program will go to the maze game window with the 40x40 maze
                   
                   if L_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the 50x50 maze button...
                       self.play_screen(50) #The program will go to the maze game window with the 50x50 maze
                   
                   if back_button.collidepoint(mouse_x, mouse_y): #If the x, y position of the mouse click was inside the "Back" button...
                       self.main_menu_screen() #return to the menus window

   def get_numeric_values(self, time): #returns a tuple value of the timer's time; first element being the minutes and the second element being the seconds
       if time is None:                #if there is no value of time, the method returns none
           return None
       else:                           
           seconds = int(time[-2:])   #finds the number of seconds by returning the last 2 values of the final time string value (slicing)
           minutes = int(time[:2])    #finds the number of minutes by returning the first 2 values of the final time string value (slicing)
           return (minutes, seconds)  #returns the tuple value for the time
   
   def compare_times(self, cb_time, recent_game_time): #checks user's time for the maze they just solved with their current best (cb) time for that maze
       best_time = cb_time                       #the best time (lowest time) is assumed to be the the current best time
       if cb_time is None:                       #checks if there is even a time to be compared with
           best_time = recent_game_time          #if there is no time to be compared with (i.e. it is "None"), the current best time is the recent time
       elif recent_game_time[0] < cb_time[0]:    #checks if the recent time's minute value is less than the current best time
           best_time = recent_game_time          #if the recent time's minute value is less than the current best time, the best time is now the recent time
       elif recent_game_time[0] == cb_time[0]:   #if the number of minutes on both times are equal, we look to compare the seconds...
           if recent_game_time[1] < cb_time[1]:  #if the seconds for the recent value is less than the  current best value, the best time is now the recent time
               best_time = recent_game_time
       
       if best_time == cb_time:                 #checks if the best time is still the current best (i.e. it remains unchanged)
           return False                         #if the best time remains unchanged, return false to state that no changes should be made to the database
       else:                                    #if the best time is changed, return true to state that changes should be made to the database
           return True

   def well_done_screen(self, maze_size, time): #This is the window which congratulates the user if they have solved the maze
       self.screen.fill(self.BLUE) #Fills the screen with the background colour to erase the contents of the previous window
       self.make_title(190, 23, "WELL DONE! YOU SOLVED THE MAZE!", 70, self.WHITE, 120) #Generates the title for this window, which congratulates the user
       self.generate_text(300, 130, f"Time taken to finish: {time}", 65, self.WHITE) #Displays the time the user took to finish by using th "display_text()" method

       current_best_time = self.user_data[str(maze_size)]  #finds the current best time for a specified maze size, using the user_data dictionary and the maze_size as a key
       
       #the method below checks if the user's current best time should be changed by seeing if the current time value is less than the current best value
       change = self.compare_times(self.get_numeric_values(current_best_time), self.get_numeric_values(time))
       
       if change: #Checks if the current best time is to be changed
           if current_best_time is not None: #This statement checks if it's the user's first time solving the maze
               self.generate_text(250, 240, f"YOU HAVE A NEW PERSONAL BEST", 65, self.WHITE)
           #the code below updates the users database and the user_data dictionary to include the new best time
           self.user_data[str(maze_size)] = time
           self.change_time(str(maze_size), time)

       #The following lines of code display buttons that give the user the choice to either go to menu, restart with a different maze size, or restart on the same maze size
       Menu_button = self.draw_button(505, 355, 290, 70, 47, "Go to Menu")
       Restart_button = self.draw_button(268, 495, 764, 70, 47, "Restart with different size maze")
       Same_Maze_button = self.draw_button(308, 635, 684, 70, 47, "Restart with same maze size")

       pygame.display.update() #Updates the pygame window to show changes

       while True: #While loop runs until user closes the window or until a button is pressed

        for event in pygame.event.get():
                if event.type == pygame.QUIT: #Checks if user has closed window
                    pygame.quit() #Pygame is quit
                    quit() #Whole program is terminated and thus the window closes
                
                elif event.type == pygame.MOUSEBUTTONDOWN: #Detects any mouse clicks/cursor clicks
                    mouse_x, mouse_y = pygame.mouse.get_pos() #returns the x, y position of the mouse click on the pygame window

                    if Menu_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Go to menu" button...
                        self.main_menu_screen() #Go to the menus window

                    if Restart_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Restart with different size maze" button...
                        self.inputs_screen() #Go to the inputs window

                    if Same_Maze_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Restart with same size maze" button...
                        self.play_screen(maze_size) #Go to the playing window with the maze size being the input

   def solving_aftermath_screen(self, maze_size):
       
       cover_up_rect = (710, 100, 600, 500)     #Erases the buttons from the previous window so that new buttons can be added
       pygame.draw.rect(self.screen, self.BLUE, cover_up_rect)

       self.make_title(480, 10, "MAZE SOLVED!", 65, self.WHITE, 90) #This is outputted to inform the user that the maze has been solved

       # The following buttons are rendered within the pygame window...
       Menu_button = self.draw_button(890, 220, 220, 55, 35, "Go to Menu") 

       Restart_button = self.draw_button(745, 350, 490, 55, 30, "Retry with different sized maze")

       Same_maze_button = self.draw_button(732, 480, 506, 55, 35, "Retry with same sized maze")

       Back_button = self.draw_button(1130, 700, 140, 70, 50, "Back")

       pygame.display.update()

       while True: #The while loop runs indefinitely until there is a mouse click or until the window is closed

        for event in pygame.event.get(): #Loks for any user input
                if event.type == pygame.QUIT: #Checks if user has closed window
                    pygame.quit() # Closes the window by terminating pygame snd the code
                    quit()
                
                elif event.type == pygame.MOUSEBUTTONDOWN: #Detects any mouse clicks/cursor clicks
                    mouse_x, mouse_y = pygame.mouse.get_pos() #returns the x, y position of the mouse click on the pygame window

                    if Menu_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Go to menu" button...
                        self.main_menu_screen() #Go to the menus window

                    if Restart_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Restart with different size maze" button...
                        self.inputs_screen() #Goes to input screen

                    if Same_maze_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Restart with same size maze" button...
                        self.play_screen(maze_size) #Restarts with the same maze
                    
                    if Back_button.collidepoint(mouse_x, mouse_y): #If x, y position of mouse click is inside the "Back" button...
                        self.inputs_screen() #Goes back to the previous window which is the inputs screen.


   def play_screen(self, maze_size):
       super().__init__(maze_size, self.max_width//maze_size) #Passes the values for the attributes onto the superclass for maze generation and maze object rendering
       self.screen.fill(self.BLUE) #Fills the window up with the background colour
       self.generate_sq_grid() #Generates the grid for the maze rendering
       self.carve_out_maze() #Randomly generates the maze
       outcome, final_time = self.make_object() #makes maze object and returns the "option" (i.e. the button clicked) as well as the total time the play window was open for

       if outcome == "BFS": #If the uset chooses to use BFS by clicking on the BFS button...
           solution_path_dict = self.BFS_algo() #BFS algo returns the solution path after analysing and processing the maze
           self.tracepath(solution_path_dict) #Traces the solution path
           self.solving_aftermath_screen(maze_size) #Takes the user to the modified window after having solved the maze

       elif outcome == "DFS":
           solution_path_dict = self.DFS_algo() #DFS algo returns the solution path after analysing and processing the maze
           self.tracepath(solution_path_dict) #Traces the solution path
           self.solving_aftermath_screen(maze_size) #Takes the user to the modified window after having solved the maze

       elif outcome == "A*":
           solution_path_dict = self.Astar_algo() #A* algo returns the solution path after analysing and processing the maze
           self.tracepath(solution_path_dict) #Traces the solution path
           self.solving_aftermath_screen(maze_size) #Takes the user to the modified window after having solved the maze

       elif outcome == "Back": 
           self.inputs_screen()
        
       elif outcome == "Solved":   #Checks if user solved the maze.
           self.well_done_screen(maze_size, final_time) #user is taken to another window if they solved the maze

game = UserInterface()
