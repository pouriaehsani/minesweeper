import pygame
import numpy as np
import random
import heapq

# تنظیمات اولیه
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Minesweeper with A* and Minimax')

# رنگ‌ها
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (192, 192, 192)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# گرفتن ورودی از کاربر
rows = int(input("ROWS : "))
cols = int(input("COLUMS : "))
mines_count = int(input("MINES : "))

# تنظیمات بازی
cell_size = 30
font = pygame.font.SysFont('Arial', 20)
board = np.zeros((rows, cols), dtype=int)
revealed = np.zeros((rows, cols), dtype=bool)
flags = np.zeros((rows, cols), dtype=bool)
mines_positions = random.sample(range(rows * cols), mines_count)

# قرار دادن بمب‌ها
for pos in mines_positions:
    board[pos // cols][pos % cols] = -1

# محاسبه اعداد مجاور بمب‌ها
def calculate_adjacent_mines():
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == -1:
                continue
            count = 0
            for r in range(max(0, row - 1), min(rows, row + 2)):
                for c in range(max(0, col - 1), min(cols, col + 2)):
                    if board[r][c] == -1:
                        count += 1
            board[row][col] = count

calculate_adjacent_mines()

# رسم بازی
def draw_board():
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * cell_size, row * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)
            if revealed[row][col]:
                if board[row][col] == -1:
                    pygame.draw.circle(screen, RED, rect.center, cell_size // 2 - 4)
                else:
                    text = font.render(str(board[row][col]), True, BLACK)
                    screen.blit(text, rect.move(10, 5))
            elif flags[row][col]:
                pygame.draw.circle(screen, BLUE, rect.center, cell_size // 2 - 4)

# تابع باز کردن خانه‌ها
def reveal_cell(row, col):
    if row < 0 or row >= rows or col < 0 or col >= cols or revealed[row][col]:
        return
    revealed[row][col] = True
    if board[row][col] == 0:
        for r in range(max(0, row - 1), min(rows, row + 2)):
            for c in range(max(0, col - 1), min(cols, col + 2)):
                reveal_cell(r, c)

# الگوریتم A*
def a_star_search(start, goal):
    open_list = []
    heapq.heappush(open_list, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_list:
        _, current = heapq.heappop(open_list)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return []

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def get_neighbors(pos):
    (x, y) = pos
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                    neighbors.append(neighbor)
    return neighbors

# الگوریتم Minimax
def minimax(board, depth, maximizing_player):
    if depth == 0 or game_over(board):
        return evaluate(board)

    if maximizing_player:
        max_eval = float('-inf')
        for move in get_all_moves(board):
            eval = minimax(move, depth - 1, False)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_all_moves(board):
            eval = minimax(move, depth - 1, True)
            min_eval = min(min_eval, eval)
        return min_eval

def game_over(board):
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == -1 and not revealed[row][col]:
                return False
    return True

def evaluate(board):
    score = 0
    for row in range(rows):
        for col in range(cols):
            if revealed[row][col]:
                score += 1
            elif board[row][col] == -1:
                score -= 1
    return score

def get_all_moves(board):
    moves = []
    for row in range(rows):
        for col in range(cols):
            if not revealed[row][col]:
                moves.append((row, col))
    return moves

# حلقه اصلی بازی
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // cell_size, x // cell_size
            if event.button == 1:  # Left click
                reveal_cell(row, col)
                if board[row][col] == -1:
                    print("Game Over!")
                    running = False
            elif event.button == 3:  # Right click
                flags[row][col] = not flags[row][col]

    screen.fill(WHITE)
    draw_board()
    pygame.display.flip()

pygame.quit()