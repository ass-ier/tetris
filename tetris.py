import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 525
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDE_PANEL_WIDTH = 220  # Increased width to accommodate content

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
DARK_GREY = (50, 50, 50)
LIGHT_GREY = (200, 200, 200)
TITLE_COLOR = (255, 215, 0)  # Gold for the title
TEXT_COLOR = (255, 255, 255)  # White for text
BORDER_COLOR = (0, 0, 0)     # Black for borders
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (255, 0, 255),  # Purple
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],                      # I
    [[1, 1], [1, 1]],                   # O
    [[0, 1, 0], [1, 1, 1]],             # T
    [[1, 0, 0], [1, 1, 1]],             # L
    [[0, 0, 1], [1, 1, 1]],             # J
    [[1, 1, 0], [0, 1, 1]],             # S
    [[0, 1, 1], [1, 1, 0]],             # Z
]

class Tetromino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = GRID_WIDTH // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def draw_window(surface, grid, score=0, next_tetromino=None, game_over=False):
    # Draw gradient background
    for i in range(SCREEN_HEIGHT):
        color = (0, 0, int(150 * (i / SCREEN_HEIGHT)))
        pygame.draw.line(surface, color, (0, i), (SCREEN_WIDTH - SIDE_PANEL_WIDTH, i))

    # Draw the game grid
    pygame.draw.rect(surface, DARK_GREY, (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 5)

    # Draw the grid squares with borders
    draw_grid(surface, grid)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(surface, BLACK, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

    # Draw the side panel background
    pygame.draw.rect(surface, LIGHT_GREY, (SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(surface, BORDER_COLOR, (SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT), 5)

    # Display the title and score
    font = pygame.font.SysFont('comicsans', 50)
    title_label = font.render('TETRIS', 1, TITLE_COLOR)
    surface.blit(title_label, (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, 20))

    font = pygame.font.SysFont('comicsans', 30)
    score_label = font.render(f'Score:', 1, TEXT_COLOR)
    surface.blit(score_label, (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, 100))

    score_value = font.render(f'{score}', 1, TEXT_COLOR)
    surface.blit(score_value, (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, 130))

    # Display the next tetromino
    if next_tetromino:
        next_label = font.render('Next:', 1, TEXT_COLOR)
        surface.blit(next_label, (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10, 200))
        next_shape = next_tetromino.shape
        for y, row in enumerate(next_shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        surface,
                        next_tetromino.color,
                        (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10 + (x * BLOCK_SIZE), 250 + (y * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE),
                        0
                    )
                    pygame.draw.rect(
                        surface,
                        BLACK,
                        (SCREEN_WIDTH - SIDE_PANEL_WIDTH + 10 + (x * BLOCK_SIZE), 250 + (y * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE),
                        1
                    )

    # Display game over message
    if game_over:
        font = pygame.font.SysFont('comicsans', 60)
        game_over_label = font.render('GAME OVER', 1, WHITE)
        surface.blit(game_over_label, (SCREEN_WIDTH // 2 - game_over_label.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_label.get_height() // 2))

        font = pygame.font.SysFont('comicsans', 40)
        final_score_label = font.render(f'Final Score: {score}', 1, WHITE)
        surface.blit(final_score_label, (SCREEN_WIDTH // 2 - final_score_label.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

def clear_rows(grid, locked_positions):
    cleared = 0
    for y in range(GRID_HEIGHT - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            cleared += 1
            for x in range(GRID_WIDTH):
                if (x, y) in locked_positions:
                    del locked_positions[(x, y)]
            # Move all rows above this one down
            for move_down_y in range(y, 0, -1):
                for x in range(GRID_WIDTH):
                    if (x, move_down_y - 1) in locked_positions:
                        locked_positions[(x, move_down_y)] = locked_positions.pop((x, move_down_y - 1))
    return cleared

def check_collision(tetromino, grid):
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                if x + tetromino.x < 0 or x + tetromino.x >= GRID_WIDTH or y + tetromino.y >= GRID_HEIGHT:
                    return True
                if grid[y + tetromino.y][x + tetromino.x] != BLACK:
                    return True
    return False

def convert_shape_format(tetromino):
    positions = []
    for y, row in enumerate(tetromino.shape):
        for x, cell in enumerate(row):
            if cell:
                positions.append((tetromino.x + x, tetromino.y + y))
    return positions

def valid_space(tetromino, grid):
    accepted_positions = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == BLACK] for y in range(GRID_HEIGHT)]
    accepted_positions = [x for item in accepted_positions for x in item]

    formatted_shape = convert_shape_format(tetromino)

    for pos in formatted_shape:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_game_over(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_tetromino = False
    run = True
    current_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    next_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.3
    score = 0
    game_over = False

    print("Game starting...")

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_tetromino.y += 1
            if not valid_space(current_tetromino, grid) and current_tetromino.y > 0:
                current_tetromino.y -= 1
                change_tetromino = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_tetromino.x -= 1
                    if not valid_space(current_tetromino, grid):
                        current_tetromino.x += 1
                if event.key == pygame.K_RIGHT:
                    current_tetromino.x += 1
                    if not valid_space(current_tetromino, grid):
                        current_tetromino.x -= 1
                if event.key == pygame.K_DOWN:
                    current_tetromino.y += 1
                    if not valid_space(current_tetromino, grid):
                        current_tetromino.y -= 1
                if event.key == pygame.K_UP:
                    current_tetromino.rotate()
                    if not valid_space(current_tetromino, grid):
                        current_tetromino.rotate()
                        current_tetromino.rotate()
                        current_tetromino.rotate()
                if event.key == pygame.K_SPACE:
                    while valid_space(current_tetromino, grid):
                        current_tetromino.y += 1
                    current_tetromino.y -= 1

        # Lock the tetromino position
        shape_pos = convert_shape_format(current_tetromino)

        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_tetromino.color

        if change_tetromino:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_tetromino.color
            current_tetromino = next_tetromino
            next_tetromino = Tetromino(random.choice(SHAPES), random.choice(COLORS))
            change_tetromino = False
            score += clear_rows(grid, locked_positions) * 10

            if check_game_over(locked_positions):
                game_over = True
                print("Game Over")

        draw_window(screen, grid, score, next_tetromino, game_over)
        pygame.display.update()

        if game_over:
            time.sleep(3)  # Wait before closing the window
            break

    pygame.display.quit()

if __name__ == '__main__':
    main()
