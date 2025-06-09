from flask import Flask, render_template, jsonify, request
import json
import random
from datetime import datetime

app = Flask(__name__)

# Tetris game logic
GRID_WIDTH = 10
GRID_HEIGHT = 20
COLORS = [
    '#00F0F0',  # Cyan
    '#0000F0',  # Blue
    '#F0A000',  # Orange
    '#F0F000',  # Yellow
    '#00F000',  # Green
    '#A000F0',  # Purple
    '#F00000',  # Red
    '#FF69B4',  # Pink (for new pieces)
    '#00CED1',  # Dark Turquoise
    '#FFD700',  # Gold
    '#FF1493',  # Deep Pink
    '#32CD32'   # Lime Green
]

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
    # 3-block L-angle (small L)
    [['.....',
      '.....',
      '.#...',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '.....',
      '.##..',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '##...',
      '.#...'],
     ['.....',
      '.....',
      '.#...',
      '##...',
      '.....']],
    # 3-block reverse L (small reverse L)
    [['.....',
      '.....',
      '.#...',
      '##...',
      '.....'],
     ['.....',
      '.....',
      '.#...',
      '.##..',
      '.....'],
     ['.....',
      '.....',
      '.....',
      '.##..',
      '.#...'],
     ['.....',
      '.....',
      '.....',
      '##...',
      '.#...']],
    # 5-block cross
    [['.....',
      '..#..',
      '.###.',
      '..#..',
      '.....']],
    # 5-block long line
    [['..#..',
      '..#..',
      '..#..',
      '..#..',
      '..#..'],
     ['.....',
      '.....',
      '#####',
      '.....',
      '.....']]
]

class TetrisGame:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.board = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.get_new_piece()
        self.next_piece = self.get_new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.fall_time = 0
        self.fall_speed = 500  # milliseconds
    
    def get_new_piece(self):
        shape_idx = random.randint(0, len(TETROMINO_SHAPES) - 1)
        rotation = 0
        return {
            'shape': TETROMINO_SHAPES[shape_idx],
            'rotation': rotation,
            'x': GRID_WIDTH // 2 - 2,
            'y': 0,
            'color': shape_idx + 1
        }
    
    def get_piece_blocks(self, piece):
        shape = piece['shape'][piece['rotation']]
        blocks = []
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell == '#':
                    blocks.append((piece['x'] + x, piece['y'] + y))
        return blocks
    
    def is_valid_position(self, piece, dx=0, dy=0, rotation=None):
        if rotation is None:
            rotation = piece['rotation']
        
        test_piece = {
            'shape': piece['shape'],
            'rotation': rotation,
            'x': piece['x'] + dx,
            'y': piece['y'] + dy,
            'color': piece['color']
        }
        
        blocks = self.get_piece_blocks(test_piece)
        
        for x, y in blocks:
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return False
            if y >= 0 and self.board[y][x]:
                return False
        
        return True
    
    def place_piece(self):
        blocks = self.get_piece_blocks(self.current_piece)
        for x, y in blocks:
            if y >= 0:
                self.board[y][x] = self.current_piece['color']
        
        lines = self.clear_lines()
        if lines > 0:
            self.lines_cleared += lines
            self.score += [0, 100, 300, 500, 800][min(lines, 4)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = max(50, 500 - (self.level - 1) * 25)
        
        self.current_piece = self.next_piece
        self.next_piece = self.get_new_piece()
        
        if not self.is_valid_position(self.current_piece):
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
    
    def move_piece(self, dx, dy=0):
        if self.game_over:
            return False
        
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece['x'] += dx
            self.current_piece['y'] += dy
            return True
        elif dy > 0:  # Piece hit bottom
            self.place_piece()
            return False
        return False
    
    def rotate_piece(self):
        if self.game_over:
            return False
        
        rotations = len(self.current_piece['shape'])
        new_rotation = (self.current_piece['rotation'] + 1) % rotations
        
        if self.is_valid_position(self.current_piece, rotation=new_rotation):
            self.current_piece['rotation'] = new_rotation
            return True
        return False
    
    def drop_piece(self):
        while self.move_piece(0, 1):
            self.score += 1
    
    def get_game_state(self):
        return {
            'board': self.board,
            'current_piece': self.current_piece,
            'next_piece': self.next_piece,
            'score': self.score,
            'level': self.level,
            'lines_cleared': self.lines_cleared,
            'game_over': self.game_over
        }

# Global game instance
game = TetrisGame()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/game_state')
def get_game_state():
    return jsonify(game.get_game_state())

@app.route('/api/move', methods=['POST'])
def move():
    data = request.get_json()
    action = data.get('action')
    
    if action == 'left':
        game.move_piece(-1)
    elif action == 'right':
        game.move_piece(1)
    elif action == 'down':
        game.move_piece(0, 1)
    elif action == 'rotate':
        game.rotate_piece()
    elif action == 'drop':
        game.drop_piece()
    elif action == 'reset':
        game.reset_game()
    
    return jsonify(game.get_game_state())

@app.route('/api/tick', methods=['POST'])
def tick():
    if not game.game_over:
        game.move_piece(0, 1)
    return jsonify(game.get_game_state())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)