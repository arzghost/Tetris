import random
from constants import COLORS, GRID_WIDTH, GRID_HEIGHT

# Define shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1],      # J
     [0, 0, 1]],
    [[1, 1, 1],      # L
     [1, 0, 0]],
    [[1, 1],         # O
     [1, 1]],
    [[0, 1, 1],      # S
     [1, 1, 0]],
    [[1, 1, 1],      # T
     [0, 1, 0]],
    [[1, 1, 0],      # Z
     [0, 1, 1]]
]

class Tetromino:
    def __init__(self):
        self.shape_idx = random.randint(0, len(SHAPES) - 1)
        self.shape = [row[:] for row in SHAPES[self.shape_idx]]
        self.color = COLORS[self.shape_idx]
        self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        """Rotate the tetromino clockwise"""
        rotated = [[self.shape[y][x] for y in range(len(self.shape)-1, -1, -1)]
                  for x in range(len(self.shape[0]))]
        return rotated

    def get_positions(self):
        """Get list of (x, y) positions of all blocks in the tetromino"""
        positions = []
        for y in range(len(self.shape)):
            for x in range(len(self.shape[0])):
                if self.shape[y][x]:
                    positions.append((self.x + x, self.y + y))
        return positions

    def is_valid_position(self, board, shape=None, x=None, y=None):
        """Check if the tetromino's position is valid"""
        if shape is None:
            shape = self.shape
        if x is None:
            x = self.x
        if y is None:
            y = self.y

        for row in range(len(shape)):
            for col in range(len(shape[0])):
                if shape[row][col]:
                    if (x + col < 0 or x + col >= GRID_WIDTH or
                        y + row >= GRID_HEIGHT or
                        (y + row >= 0 and board[y + row][x + col])):
                        return False
        return True
