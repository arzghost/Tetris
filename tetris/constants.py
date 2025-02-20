# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Tetromino colors
COLORS = [
    (0, 240, 240),  # Cyan
    (0, 0, 240),    # Blue
    (240, 160, 0),  # Orange
    (240, 240, 0),  # Yellow
    (0, 240, 0),    # Green
    (160, 0, 240),  # Purple
    (240, 0, 0)     # Red
]

# Game dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # Extra space for next piece and score
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

# Game settings
FPS = 60
MOVE_DELAY = 100  # Milliseconds between moves
SOFT_DROP_DELAY = 50
INITIAL_FALL_SPEED = 1000  # Milliseconds between automatic drops
LEVEL_SPEEDUP = 0.8  # Multiply fall speed by this each level

# Scoring system
POINTS = {
    1: 100,    # Single line
    2: 300,    # Double
    3: 500,    # Triple
    4: 800     # Tetris
}
