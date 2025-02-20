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
        self.small_font = pygame.font.Font(None, 24)  # Smaller font for controls
        self.sounds = SoundEffects()

        self.difficulty = "Medium"  # Default difficulty
        self.show_menu = True
        self.reset_game()

    def reset_game(self):
        self.board = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = DIFFICULTY_LEVELS[self.difficulty]["fall_speed"]
        self.last_fall = pygame.time.get_ticks()
        self.last_move = pygame.time.get_ticks()

    def handle_menu_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                    difficulties = list(DIFFICULTY_LEVELS.keys())
                    current_idx = difficulties.index(self.difficulty)
                    if event.key == pygame.K_UP:
                        self.difficulty = difficulties[(current_idx - 1) % len(difficulties)]
                    else:
                        self.difficulty = difficulties[(current_idx + 1) % len(difficulties)]
                elif event.key == pygame.K_RETURN:
                    self.show_menu = False
                    self.reset_game()
        return True

    def handle_game_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_menu = True  # Return to menu instead of quitting
                    return True
                if event.key == pygame.K_p:  # Toggle pause
                    self.paused = not self.paused
                elif event.key == pygame.K_r:  # Reset game
                    self.reset_game()
                elif not self.game_over and not self.paused:
                    if event.key == pygame.K_LEFT:
                        self.move(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.move(1)
                    elif event.key == pygame.K_UP:
                        self.rotate_piece()
                    elif event.key == pygame.K_SPACE:
                        self.hard_drop()

        # Handle soft drop
        if not self.game_over and not self.paused and pygame.key.get_pressed()[pygame.K_DOWN]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_fall >= SOFT_DROP_DELAY:
                self.move_down()
                self.last_fall = current_time

        return True

    def draw_menu(self):
        self.screen.fill(BLACK)

        # Draw title
        title = self.font.render("TETRIS", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title, title_rect)

        # Draw difficulty options
        y_offset = SCREEN_HEIGHT // 2
        for diff in DIFFICULTY_LEVELS.keys():
            color = WHITE if diff == self.difficulty else GRAY
            text = self.font.render(diff, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 50

        # Draw instructions
        instructions = self.small_font.render("↑↓ to select, ENTER to start", True, WHITE)
        inst_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, y_offset + 30))
        self.screen.blit(instructions, inst_rect)

        pygame.display.flip()

    def draw(self):
        self.screen.fill(BLACK)

        # Draw frame around play field
        pygame.draw.rect(self.screen, WHITE, 
                        (0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE), 2)

        # Draw frame around right panel
        preview_x = GRID_WIDTH * BLOCK_SIZE + 20
        preview_width = SCREEN_WIDTH - preview_x - 20
        pygame.draw.rect(self.screen, WHITE,
                        (preview_x, 0, preview_width, SCREEN_HEIGHT), 2)

        # Draw game board
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.board[y][x]
                if color:
                    pygame.draw.rect(self.screen, color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw current piece
        if not self.paused:
            for x, y in self.current_piece.get_positions():
                if y >= 0:
                    pygame.draw.rect(self.screen, self.current_piece.color,
                                   (x * BLOCK_SIZE, y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw next piece preview
        preview_x = GRID_WIDTH * BLOCK_SIZE + 30
        preview_y = 50
        self.screen.blit(self.font.render("Next:", True, WHITE), (preview_x, 10))
        if not self.paused:
            for y in range(len(self.next_piece.shape)):
                for x in range(len(self.next_piece.shape[0])):
                    if self.next_piece.shape[y][x]:
                        pygame.draw.rect(self.screen, self.next_piece.color,
                                       (preview_x + x * BLOCK_SIZE,
                                        preview_y + y * BLOCK_SIZE,
                                        BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Draw score, level and difficulty
        self.screen.blit(self.font.render(f"Score: {self.score}", True, WHITE),
                        (preview_x, preview_y + 120))
        self.screen.blit(self.font.render(f"Level: {self.level}", True, WHITE),
                        (preview_x, preview_y + 160))
        self.screen.blit(self.font.render(f"Difficulty: {self.difficulty}", True, WHITE),
                        (preview_x, preview_y + 200))

        # Draw controls
        self.draw_controls(preview_x, preview_y + 240)

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, WHITE)
            restart_text = self.font.render("Press R to restart", True, WHITE)
            self.screen.blit(game_over_text,
                           (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text,
                           (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 + 10))
        elif self.paused:
            pause_text = self.font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_text,
                           (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                            SCREEN_HEIGHT // 2))

        pygame.display.flip()

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
            # Apply difficulty multiplier to score
            multiplier = DIFFICULTY_LEVELS[self.difficulty]["score_multiplier"]
            self.score += int(POINTS[len(lines_to_clear)] * self.level * multiplier)
            self.level = self.lines_cleared // 10 + 1
            # Apply difficulty speedup
            speedup = DIFFICULTY_LEVELS[self.difficulty]["speedup"]
            self.fall_speed = int(DIFFICULTY_LEVELS[self.difficulty]["fall_speed"] * 
                                (speedup ** (self.level - 1)))

    def run(self):
        while True:
            if self.show_menu:
                if not self.handle_menu_input():
                    break
                self.draw_menu()
            else:
                if not self.handle_game_input():
                    break

                current_time = pygame.time.get_ticks()
                if not self.game_over and not self.paused and current_time - self.last_fall >= self.fall_speed:
                    self.move_down()
                    self.last_fall = current_time

                self.draw()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def draw_controls(self, x, y):
        """Draw the game controls information in the side panel"""
        controls = [
            "Controls:",
            "Left/Right - Move",
            "Up - Rotate",
            "Down - Soft Drop",
            "Space - Hard Drop",
            "P - Pause",
            "R - Restart",
            "ESC - Exit"
        ]

        for i, text in enumerate(controls):
            surface = self.small_font.render(text, True, WHITE)
            self.screen.blit(surface, (x, y + i * 25))


if __name__ == "__main__":
    game = TetrisGame()
    game.run()