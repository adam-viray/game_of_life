# -*- coding: utf-8 -*-
"""
Game of Life
17 January 2021
"""

import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
plt.style.use("fivethirtyeight")

P = 0
col = int(input("Width of grid:\n"))
row = int(input("Height of grid:\n"))
conf = int(input("Which initial configuration would you like to use?\n"
                 "    0. Random\n    1. Shape 1\n    2. Shape 2\n    3. Shape 3\n    4. Shape 4\n    5. Shape 5\n    6. Shape 6\n    7. Shape 7\n"))
if conf == 0:
    P = float(input("What decimal probability does each cell have of being alive?\n"))
bc = int(input("Select boundary condition: periodic = 1, fixed = 2\n"))
if bc == 1:
    bc = "wrap"
else:
    bc = "symm"
    
#initialize arrays "grid" and "grid_next"
def construct(col, row, conf, P):
    global grid,grid_next,dt0,dt1
    x,y = (col//2)-1,(row//2)-1
    grid = np.zeros((row,col), dtype=np.int8)    
    if conf == 0:
        grid = np.random.default_rng().choice([0,1], size=(row,col), replace=True, p=[P, 1-P])
    elif conf == 1:
        grid[y][x],grid[y][x-1],grid[y][x+1] = 1,1,1
    elif conf == 2:
        grid[y][x],grid[y-1][x],grid[y][x+1] = 1,1,1
    elif conf == 3:
        grid[y][x],grid[y][x-1],grid[y][x+1],grid[y][x+2] = 1,1,1,1
    elif conf == 4:
        grid[y][x],grid[y+1][x],grid[y][x-1],grid[y][x+1] = 1,1,1,1
    elif conf == 5:
        grid[y][x],grid[y-2][x],grid[y-1][x+1],grid[y][x-1],grid[y][x+1] = 1,1,1,1,1
    elif conf == 6:
        grid[y][x],grid[y+1][x],grid[y-1][x],grid[y-1][x+1],grid[y][x-1] = 1,1,1,1,1
    elif conf == 7:
        grid[y][x],grid[y][x-1],grid[y][x+1],grid[y-1][x],grid[y-1][x+1],grid[y-1][x+2] = 1,1,1,1,1,1
    grid_next = np.zeros((row,col), dtype=np.int8)
    dt0, dt1 = [], []

        
#tally nearest and next-nearest neighbors
def neighbors(i, j, bc):
    right = col - 1
    bottom = row - 1
    k = 0
    
    if i == 0 and j == 0:
        #top left edge case
        if bc == "wrap":
            neighbors = [grid[bottom][right], grid[i][right], grid[i+1][right], grid[bottom][j], grid[i+1][j], grid[bottom][j+1], grid[i][j+1], grid[i+1][j+1]]
        else:
            neighbors = [grid[i][j+1], grid[i+1][j][i+1][j+1]]
    elif i == bottom and j == 0:
        #bottom left edge case
        if bc == "wrap":
            neighbors = [grid[i-1][right], grid[i][right], grid[0][right], grid[i-1][j], grid[0][j], grid[i-1][j+1], grid[i][j+1], grid[0][j+1]]
        else:
            neighbors = [grid[i-1][j], grid[i-1][j+1], grid[i][j+1]]
    elif i == 0 and j == right:
        #top right edge case
        if bc == "wrap":
            neighbors = [grid[bottom][j-1], grid[i][j-1], grid[i+1][j-1], grid[bottom][j], grid[i+1][j], grid[bottom][0], grid[i][0], grid[i+1][0]]
        else:
            neighbors= [grid[i][j-1], grid[i+1][j-1], grid[i+1][j]]
    elif i == bottom and j == right:
        #bottom right edge case
        if bc == "wrap":
            neighbors = [grid[i-1][j-1], grid[i][j-1], grid[0][j-1], grid[i-1][j], grid[0][j], grid[i-1][0], grid[i][0], grid[0][0]]
        else:
            neighbors = [grid[i-1][j-1], grid[i-1][j], grid[i][j-1]]
    elif i == 0:
        #top edge case
        if bc == "wrap":
            neighbors = [grid[bottom][j-1], grid[i][j-1], grid[i+1][j-1], grid[bottom][j], grid[i+1][j], grid[bottom][j+1], grid[i][j+1], grid[i+1][j+1]]
        else:
            neighbors = [grid[i][j-1], grid[i][j+1], grid[i+1][j-1], grid[i+1][j], grid[i+1][j+1]]
    elif i == bottom:
        #bottom edge case
        if  bc == "wrap":
            neighbors = [grid[i-1][j-1], grid[i][j-1], grid[0][j-1], grid[i-1][j], grid[0][j], grid[i-1][j+1], grid[i][j+1], grid[0][j+1]]
        else:
            neighbors = [grid[i-1][j-1], grid[i-1][j], grid[i-1][j+1], grid[i][j-1], grid[i][j+1]]
    elif j == 0:
        #left edge case
        if bc == "wrap":
            neighbors = [grid[i-1][right], grid[i][right], grid[i+1][right], grid[i-1][j], grid[i+1][j], grid[i-1][j+1], grid[i][j+1], grid[i+1][j+1]]
        else:
            neighbors = [grid[i-1][j], grid[i-1][j+1], grid[i][j+1], grid[i+1][j], grid[i+1][j+1]]
    elif j == right:
        #right edge case
        if bc == "wrap":
            neighbors = [grid[i-1][j-1], grid[i][j-1], grid[i+1][j-1], grid[i-1][j], grid[i+1][j], grid[i-1][0], grid[i][0], grid[i+1][0]]
        else:
            neighbors = [grid[i-1][j-1], grid[i-1][j], grid[i][j-1], grid[i+1][j-1], grid[i+1][j]]
    else:
        #normal case
        neighbors = [grid[i-1][j-1], grid[i-1][j-1], grid[i-1][j+1], grid[i][j-1], grid[i][j+1], grid[i+1][j-1], grid[i+1][j], grid[i+1][j+1]]
    
    for n in neighbors:
        k += n
    return k

#play life
def life(f):
    #make changes in grid_next array
    for i in range(row):
        for j in range(col):
            n = neighbors(i,j,bc)
            if grid[i][j] == 0:
                if n == 3:
                    grid_next[i][j] = 1
                else:
                    grid_next[i][j] = 0
            else:
                if n == 2 or n == 3:
                    grid_next[i][j] = 1
                else:
                    grid_next[i][j] = 0
    
    dt0.append((np.mean(grid) * 100))
    dt1.append((np.mean(grid_next) * 100))
    
    im.set_array(grid)
    sc.set_data(dt0,dt1)
    ax1.relim
    ax1.autoscale_view(True, True, True)
    
    for h in range(row):
        for j in range(col):
            grid[h][j] = grid_next[h][j]
            
    return im, sc,
    #return sc,

def main():    
    global im, sc, ax1
    construct(col, row, conf, P)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    im = ax2.imshow(grid, animated=True)
    sc, = ax1.plot(0, 0, marker='o', ls="")

    anim = FuncAnimation(fig, life, frames=100, interval=120, blit=True)
    plt.show()

if __name__ == "__main__":
    main()
