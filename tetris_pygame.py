import pygame
import sys
import os
import random
from enum import Enum

# Set up display for headless environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['DISPLAY'] = ':99'

# Initialize pygame
pygame.init()
pygame.mixer.quit()  # Disable audio to avoid issues

# Constants
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

COLORS = [
    (0, 0, 0),      # Empty - Black
    (0, 240, 240),  # Cyan
    (0, 0, 240),    # Blue
    (240, 160, 0),  # Orange
    (240, 240, 0),  # Yellow
    (0, 240, 0),    # Green
    (160, 0, 240),  # Purple
    (240, 0, 0),    # Red
    (255, 105, 180), # Pink (new pieces)
    (0, 206, 209),   # Dark Turquoise
    (255, 215, 0),   # Gold
    (255, 20, 147),  # Deep Pink
    (50, 205, 50)    # Lime Green
]

# Tetromino shapes
TETROMINO_SHAPES = [
    # I-piece (4 blocks)
    [['.....',
      '..#..',
      '..#..',
      '..#..',
      '..#..'],
     ['.....',
      '.....',
      '####.',
      '.....',
      '.....']],
    # O-piece
    [['.....',
      '.....',
      '.##..',
      '.##..',
      '.....']],
    # T-piece
    [['.....',
      '.....',
      '.#...',
      '###..',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '.#...'],
     ['.....',
      '.....',
      '.#...',
      '##...',
      '.#...']],
    # S-piece
    [['.....',
      '.....',
      '.##..',
      '##...',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '..#..']],
    # Z-piece
    [['.....',
      '.....',
      '##...',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '..#..',
      '.##..',
      '.#...']],
    # J-piece
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '##...'],
     ['.....',
      '.....',
      '#....',
      '###..',
      '.....'],
     ['.....',
      '.....',
      '.##..',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '..#..']],
    # L-piece
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '.##..'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '#....'],
     ['.....',
      '.....',
      '##...',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '..#..',
      '###..',
      '.....']],
    # 3-block line
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '###..',
      '.....']],
    # 3-block L-angle (left)
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '##...'],
     ['.....',
      '.....',
      '#....',
      '##...',
      '.....'],
     ['.....',
      '.....',
      '.##..',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '##...',
      '..#..']],
    # 3-block L-angle (right)
    [['.....',
      '.....',
      '.#...',
      '.#...',
      '.##..'],
     ['.....',
      '.....',
      '.....',
      '##...',
      '#....'],
     ['.....',
      '.....',
      '##...',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '..#..',
      '##...',
      '.....']],
    # 5-block cross
    [['.....',
      '..#..',
      '.###.',
      '..#..',
      '.....']],
    # 5-block long line
    [['.....',
      '.#...',
      '.#...',
      '.#...',
      '.#...'],
     ['.....',
      '.....',
      '#####',
      '.....',
      '.....']]
]

class Tetromino:
    def __init__(self):
        self.shape_index = random.randint(0, len(TETROMINO_SHAPES) - 1)
        self.shape = TETROMINO_SHAPES[self.shape_index]
        self.rotation = 0
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0
        self.color = self.shape_index + 1

    def get_blocks(self):
        shape = self.shape[self.rotation]
        blocks = []
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    blocks.append((self.x + x, self.y + y))
        return blocks

    def is_valid_position(self, board, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = self.rotation
        
        test_shape = self.shape[rotation]
        
        for y, row in enumerate(test_shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    new_x = self.x + x + dx
                    new_y = self.y + y + dy
                    
                    if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                        return False
                    if new_y >= 0 and board[new_y][new_x]:
                        return False
        return True

    def rotate(self):
        new_rotation = (self.rotation + 1) % len(self.shape)
        return new_rotation

class TetrisGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris - Extended Version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.reset_game()

    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500
        self.last_fall = pygame.time.get_ticks()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_game()
                elif not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move_piece(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_piece(1, 0)
                    elif event.key == pygame.K_DOWN:
                        self.move_piece(0, 1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
        return True

    def move_piece(self, dx, dy):
        if self.current_piece.is_valid_position(self.board, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        elif dy > 0:  # Piece hit bottom
            self.place_piece()
            return False
        return False

    def rotate_piece(self):
        new_rotation = self.current_piece.rotate()
        if self.current_piece.is_valid_position(self.board, rotation=new_rotation):
            self.current_piece.rotation = new_rotation

    def hard_drop(self):
        while self.move_piece(0, 1):
            self.score += 1

    def place_piece(self):
        blocks = self.current_piece.get_blocks()
        for x, y in blocks:
            if y >= 0:
                self.board[y][x] = self.current_piece.color

        lines = self.clear_lines()
        if lines > 0:
            self.lines_cleared += lines
            self.score += [0, 100, 300, 500, 800][min(lines, 4)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 25)

        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        if not self.current_piece.is_valid_position(self.board):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)

        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(GRID_WIDTH)])

        return len(lines_to_clear)

    def update(self):
        if not self.game_over:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_fall >= self.fall_speed:
                self.move_piece(0, 1)
                self.last_fall = current_time

    def draw(self):
        self.screen.fill(BLACK)

        # Draw game board border
        pygame.draw.rect(self.screen, WHITE, 
                        (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

        # Draw placed blocks
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.board[y][x]:
                    color = COLORS[self.board[y][x]]
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        if not self.game_over:
            blocks = self.current_piece.get_blocks()
            color = COLORS[self.current_piece.color]
            for x, y in blocks:
                if y >= 0:
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw side panel
        panel_x = GRID_WIDTH * BLOCK_SIZE + 20
        
        # Draw next piece
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (panel_x, 20))
        
        next_shape = self.next_piece.shape[0]
        next_color = COLORS[self.next_piece.color]
        for y, row in enumerate(next_shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    pygame.draw.rect(self.screen, next_color,
                                   (panel_x + x * 20, 60 + y * 20, 18, 18))

        # Draw score and stats
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        
        self.screen.blit(score_text, (panel_x, 180))
        self.screen.blit(level_text, (panel_x, 220))
        self.screen.blit(lines_text, (panel_x, 260))

        # Draw controls
        controls = [
            "Controls:",
            "← → Move",
            "↑ Rotate", 
            "↓ Soft Drop",
            "Space Hard Drop",
            "R Restart",
            "ESC Quit"
        ]
        
        for i, text in enumerate(controls):
            color = WHITE if i == 0 else GRAY
            control_text = self.small_font.render(text, True, color)
            self.screen.blit(control_text, (panel_x, 320 + i * 25))

        # Draw game over
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                            SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text,
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 + 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()