import sys
import pygame
import math
import random
from pygame.locals import *

GAME_NAME = "Minecraft Sweeper"
FPS = 60
WINDOW_SIZE = (1280, 720)

BOARD_SIZE = (8, 8)
MINE_COUNT = 5

MAIN_BOARD_PERCENTAGE = 0.8

if WINDOW_SIZE[1] / WINDOW_SIZE[0] > BOARD_SIZE[1] / BOARD_SIZE[0]:
    SQUARE_SIZE = WINDOW_SIZE[0] * MAIN_BOARD_PERCENTAGE / BOARD_SIZE[0]
else:
    SQUARE_SIZE = WINDOW_SIZE[1] * MAIN_BOARD_PERCENTAGE / BOARD_SIZE[1]

BLACK = (0,0,0)
RED = (255,0,0)
GRAY = (170,170,170)
LIGHTGRAY = (204,204,204)
WHITE = (255,255,255)

text_sprites = []
text_sizes = []

game_board = []
flags = []
is_first_mine = True

gameover = False

def init_texts():
    global text_sprites
    text_sprites.append(font.render("!", True, RED))
    text_sizes.append(font.size("!"))

    for i in range(1, 9):
        text_sprites.append(font.render(str(i), True, BLACK))
        text_sizes.append(font.size(str(i)))

def draw_square(x, y, bg = 0, fg = 0):
    real_x = WINDOW_SIZE[0] / 2 + SQUARE_SIZE * (x - BOARD_SIZE[0] / 2 + 1 / 2)
    real_y = WINDOW_SIZE[1] / 2 + SQUARE_SIZE * (y - BOARD_SIZE[1] / 2 + 1 / 2)

    pygame.draw.rect(game_display, GRAY,
                    (real_x - SQUARE_SIZE / 2, real_y - SQUARE_SIZE / 2,
                    SQUARE_SIZE, SQUARE_SIZE))
    
    if bg == 0:
        pygame.draw.rect(game_display, LIGHTGRAY,
                    (real_x - SQUARE_SIZE * 0.9 / 2, real_y - SQUARE_SIZE * 0.9 / 2,
                    SQUARE_SIZE * 0.9, SQUARE_SIZE * 0.9))
        
    if fg == -1:
         pygame.draw.circle(game_display, BLACK,
                    (real_x, real_y),
                    SQUARE_SIZE * 0.3)
         return
         
    if fg == -2:
        game_display.blit(text_sprites[0], (real_x - text_sizes[0][0] / 2, real_y - text_sizes[0][1] / 2))

    if fg > 0:
        game_display.blit(text_sprites[fg], (real_x - text_sizes[fg][0] / 2, real_y - text_sizes[fg][1] / 2))

def init_board():
    global game_board, flags, gameover, is_first_mine
    gameover = False
    is_first_mine = True
    game_board = []
    flags = []
    for i in range(BOARD_SIZE[0]):
        line = []
        for j in range(BOARD_SIZE[1]):
            line.append(0)
        game_board.append(line)

def reset_game():
    init_board()
    add_mine(MINE_COUNT)
    draw_board()

def add_mine(count):
    while count > 0:
        rand_x = random.randint(0, BOARD_SIZE[0] - 1)
        rand_y = random.randint(0, BOARD_SIZE[1] - 1)

        if game_board[rand_x][rand_y] == 0:
            game_board[rand_x][rand_y] = -1
            count -= 1

def draw_board():
    for x in range(0, BOARD_SIZE[0]):
        for y in range(0, BOARD_SIZE[1]):
            draw_square(x, y)

def get_square(x, y):
    if x < 0 or x >= BOARD_SIZE[0] or y < 0 or y >= BOARD_SIZE[1]:
        return -1
    if game_board[x][y] == -1:
        return 1
    return 0

def get_near_mine(x, y):
    def get_mine(dx, dy):
        xx = x + dx
        yy = y + dy
        mine = get_square(xx, yy)

        if mine == 1:
            return 1
        return 0
    
    total_mine = 0
    total_mine += get_mine(-1, -1)
    total_mine += get_mine(-1, 0)
    total_mine += get_mine(-1, 1)
    total_mine += get_mine(0, -1)
    total_mine += get_mine(0, 1)
    total_mine += get_mine(1, -1)
    total_mine += get_mine(1, 0)
    total_mine += get_mine(1, 1)

    return total_mine


def reveal_all_mines(bg=0):
    for x in range(0, BOARD_SIZE[0]):
        for y in range(0, BOARD_SIZE[1]):
            if game_board[x][y] == -1:
                draw_square(x, y, bg, -1)

def open_safe_tiles(x, y):
    if get_near_mine(x, y) > 0:
        return
    
    open_list = []
    next_open_list = []

    def add(xx, yy):
        if get_square(xx, yy) != -1 and game_board[xx][yy] == 0:
            next_open_list.append((xx, yy))

    def add_near(xx, yy):
        add(xx - 1, yy - 1)
        add(xx - 1, yy)
        add(xx - 1, yy + 1)
        add(xx, yy - 1)
        add(xx, yy + 1)
        add(xx + 1, yy - 1)
        add(xx + 1, yy)
        add(xx + 1, yy + 1)
        

    def open(xx, yy):
        square = get_square(xx, yy)
        if square == -1:
            return
        if game_board[xx][yy] == 1:
            return
        
        mine = get_near_mine(xx, yy)

        game_board[xx][yy] = 1
        draw_square(xx, yy, 1, mine)
        
        if mine == 0:
            add_near(xx, yy)

    add_near(x, y)

    while len(next_open_list) > 0:
        open_list = next_open_list
        next_open_list = []
        for new_x, new_y in open_list:
            open(new_x, new_y)
    
    


def convert_pos_to_square(x, y):
    xx = (x - WINDOW_SIZE[0] / 2) / SQUARE_SIZE + BOARD_SIZE[0] / 2
    yy = (y - WINDOW_SIZE[1] / 2) / SQUARE_SIZE + BOARD_SIZE[1] / 2
    return (xx, yy)

def check_clear():
    global gameover
    for line in game_board:
        if 0 in line:
            return
        
    gameover = 1

    reveal_all_mines(1)

def button_click_event(x, y, button):
    global gameover, is_first_mine
    if gameover:
        reset_game()
        return

    xx, yy = convert_pos_to_square(x, y)

    idx_x = int(xx)
    idx_y = int(yy)

    if (xx - idx_x - 1 / 2) > 0.45 or (yy - idx_y - 1 / 2) > 0.45:
        return
    
    if idx_x < 0 or idx_x >= BOARD_SIZE[0] or idx_y < 0 or idx_y >= BOARD_SIZE[1]:
        return
    
    if button == 1:
        if (idx_x, idx_y) in flags:
            return
        squaretype = game_board[idx_x][idx_y]
        if squaretype == -1:
            if is_first_mine:
                is_first_mine = False
                while game_board[idx_x][idx_y] == -1:
                    game_board[idx_x][idx_y] = 0
                    add_mine(1)
                button_click_event(x, y, button)
                return
            reveal_all_mines()
            gameover = True
        elif squaretype == 0:
            is_first_mine = False
            game_board[idx_x][idx_y] = 1
            draw_square(idx_x, idx_y, 1, get_near_mine(idx_x, idx_y))
            open_safe_tiles(idx_x, idx_y)
            check_clear()

    if button == 3:
        if game_board[idx_x][idx_y] == 1:
            return
        if (idx_x, idx_y) in flags:
            draw_square(idx_x, idx_y, 0, 0)
            flags.remove((idx_x, idx_y))
        else:
            draw_square(idx_x, idx_y, 0, -2)
            flags.append((idx_x, idx_y))
            
            

if __name__ == "__main__":
    pygame.init()

    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, int(SQUARE_SIZE))

    init_texts()

    game_display = pygame.display.set_mode(WINDOW_SIZE)
    game_display.fill(WHITE)
    pygame.display.set_caption(GAME_NAME)


    reset_game()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                button_click_event(event.pos[0], event.pos[1], event.button)
        clock.tick(FPS)

        pygame.display.update()
