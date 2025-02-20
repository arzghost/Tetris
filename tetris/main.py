import pygame
import sys
from constants import *
from tetromino import Tetromino
from sounds import SoundEffects

class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.sounds = SoundEffects()
        
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = INITIAL_FALL_SPEED
        self.last_fall = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()
                elif event.key == pygame.K_r:
                    self.reset_game()

        # Handle soft drop
        if not self.game_over and pygame.key.get_pressed()[pygame.K_DOWN]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_fall >= SOFT_DROP_DELAY:
                self.move_down()
                self.last_fall = current_time

        return True

    def move(self, dx):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move < MOVE_DELAY:
            return

        self.current_piece.x += dx
        if not self.current_piece.is_valid_position(self.board):
            self.current_piece.x -= dx
        else:
            self.sounds.play_move()
            self.last_move = current_time

    def rotate_piece(self):
        rotated = self.current_piece.rotate()
        if self.current_piece.is_valid_position(self.board, shape=rotated):
            self.current_piece.shape = rotated
            self.sounds.play_rotate()

    def move_down(self):
        self.current_piece.y += 1
        if not self.current_piece.is_valid_position(self.board):
            self.current_piece.y -= 1
            self.freeze_piece()
            return False
        return True

    def hard_drop(self):
        while self.move_down():
            pass
        self.sounds.play_drop()

    def freeze_piece(self):
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                self.board[y][x] = self.current_piece.color
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        
        if not self.current_piece.is_valid_position(self.board):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = []
        for y in range(GRID_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        if lines_to_clear:
            self.sounds.play_clear()
            for y in lines_to_clear:
                del self.board[y]
                self.board.insert(0, [None for _ in range(GRID_WIDTH)])
            
            self.lines_cleared += len(lines_to_clear)
            self.score += POINTS[len(lines_to_clear)] * self.level
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = int(INITIAL_FALL_SPEED * (LEVEL_SPEEDUP ** (self.level - 1)))

    def draw(self):
        self.screen.fill(BLACK)

        # Draw frame around play field
        pygame.draw.rect(self.screen, WHITE, 
                        (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

        # Draw game board
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board[y][x]
                if color:
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        for x, y in self.current_piece.get_positions():
            if y >= 0:
                pygame.draw.rect(self.screen, self.current_piece.color,
                               (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + 30
        preview_y = 50
        self.screen.blit(self.font.render("Next:", True, WHITE), (preview_x, 10))
        for y in range(len(self.next_piece.shape)):
            for x in range(len(self.next_piece.shape[0])):
                if self.next_piece.shape[y][x]:
                    pygame.draw.rect(self.screen, self.next_piece.color,
                                   (preview_x + x * BLOCK_SIZE,
                                    preview_y + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw score and level
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE),
                        (preview_x, preview_y + 120))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE),
                        (preview_x, preview_y + 160))

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
        while True:
            if not self.handle_input():
                break

            current_time = pygame.time.get_ticks()
            if not self.game_over and current_time - self.last_fall >= self.fall_speed:
                self.move_down()
                self.last_fall = current_time

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()