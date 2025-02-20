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

# Difficulty settings
DIFFICULTY_LEVELS = {
    "Easy": {
        "fall_speed": 1000,    # Initial fall speed in milliseconds
        "speedup": 0.9,        # Level speedup multiplier
        "score_multiplier": 1   # Score multiplier
    },
    "Medium": {
        "fall_speed": 800,
        "speedup": 0.8,
        "score_multiplier": 1.5
    },
    "Hard": {
        "fall_speed": 500,
        "speedup": 0.7,
        "score_multiplier": 2
    }
}

# Scoring system
POINTS = {
    1: 100,    # Single line
    2: 300,    # Double
    3: 500,    # Triple
    4: 800     # Tetris
}