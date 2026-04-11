from __future__ import annotations

import math
import random

import pygame

from .resources import FontBundle, create_font_bundle, initialize_runtime, shutdown_runtime


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
DARK_GRAY = (50, 50, 50)
BOMB_COLOR = (255, 100, 0)
BACKGROUND_COLOR = (40, 40, 60)
WINDOW_CAPTION = "俄罗斯方块"

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1]],
]

COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED, BOMB_COLOR]
BOMB_INDEX = 7
BOMB_PROBABILITY = 1 / 15

GAME_AREA_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - GRID_WIDTH * GRID_SIZE) // 2
GAME_AREA_Y = (SCREEN_HEIGHT - GRID_HEIGHT * GRID_SIZE) // 2


class Tetromino:
    def __init__(self) -> None:
        self.shape_index = BOMB_INDEX if random.random() < BOMB_PROBABILITY else random.randint(0, 6)
        self.shape = [row[:] for row in SHAPES[self.shape_index]]
        self.color = COLORS[self.shape_index]

        if self.shape_index == BOMB_INDEX:
            self.x = GRID_WIDTH // 2
            self.y = 0
        else:
            self.x = GRID_WIDTH // 2 - len(self.shape[0]) // 2
            self.y = 0

    def rotate(self) -> list[list[int]] | None:
        if self.shape_index == BOMB_INDEX:
            return None

        rows = len(self.shape)
        cols = len(self.shape[0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for row_index in range(rows):
            for col_index in range(cols):
                rotated[col_index][rows - 1 - row_index] = self.shape[row_index][col_index]
        return rotated

    def draw(self, surface: pygame.Surface) -> None:
        for row_index, row in enumerate(self.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                rect = pygame.Rect(
                    GAME_AREA_X + (self.x + col_index) * GRID_SIZE,
                    GAME_AREA_Y + (self.y + row_index) * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                )

                if self.shape_index == BOMB_INDEX:
                    pygame.draw.rect(surface, self.color, rect)
                    pygame.draw.rect(surface, WHITE, rect, 1)
                    fuse_rect = pygame.Rect(rect.x + GRID_SIZE // 2 - 2, rect.y - 5, 4, 8)
                    pygame.draw.rect(surface, YELLOW, fuse_rect)
                    spark_points = [
                        (rect.x + GRID_SIZE // 2, rect.y - 10),
                        (rect.x + GRID_SIZE // 2 - 5, rect.y - 15),
                        (rect.x + GRID_SIZE // 2 + 5, rect.y - 15),
                    ]
                    pygame.draw.polygon(surface, YELLOW, spark_points)
                    continue

                pygame.draw.rect(surface, self.color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)
                highlight = pygame.Rect(rect.x + 2, rect.y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
                pygame.draw.rect(surface, self._adjust_color(self.color, 50), highlight, 1)

    @staticmethod
    def _adjust_color(color: tuple[int, int, int], adjustment: int) -> tuple[int, int, int]:
        return tuple(max(0, min(255, channel + adjustment)) for channel in color)


class Game:
    def __init__(self, fonts: FontBundle) -> None:
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.fall_speed = 0.5
        self.fall_time = 0.0
        self.paused = False

        self.explosion_active = False
        self.explosion_time = 0.0
        self.explosion_positions: list[tuple[int, int]] = []

        self.key_states = {
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
            pygame.K_DOWN: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_s: False,
        }

        self.key_delay = 0.15
        self.key_interval = 0.05
        self.key_timers = {
            pygame.K_LEFT: 0.0,
            pygame.K_RIGHT: 0.0,
            pygame.K_DOWN: 0.0,
            pygame.K_a: 0.0,
            pygame.K_d: 0.0,
            pygame.K_s: 0.0,
        }

        self.font = fonts.body
        self.small_font = fonts.small
        self.big_font = fonts.title

    def new_piece(self) -> None:
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()
        if self.check_collision(self.current_piece):
            self.game_over = True

    def check_collision(self, piece: Tetromino, dx: int = 0, dy: int = 0) -> bool:
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                new_x = piece.x + col_index + dx
                new_y = piece.y + row_index + dy
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return True
                if new_y >= 0 and self.grid[new_y][new_x]:
                    return True
        return False

    def explode_bomb(self, x: int, y: int) -> None:
        self.explosion_positions = []
        explosion_offsets = [
            (-1, -1),
            (0, -1),
            (1, -1),
            (-1, 0),
            (1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
        ]
        for offset_x, offset_y in explosion_offsets:
            new_x = x + offset_x
            new_y = y + offset_y
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                self.grid[new_y][new_x] = 0
                self.explosion_positions.append((new_x, new_y))
        self.explosion_active = True
        self.explosion_time = 0.0

    def lock_piece(self) -> None:
        if self.current_piece.shape_index == BOMB_INDEX:
            self.explode_bomb(self.current_piece.x, self.current_piece.y)
            self.new_piece()
            return

        for row_index, row in enumerate(self.current_piece.shape):
            for col_index, cell in enumerate(row):
                if cell and self.current_piece.y + row_index >= 0:
                    self.grid[self.current_piece.y + row_index][self.current_piece.x + col_index] = self.current_piece.color

        self.clear_lines()
        self.new_piece()

    def clear_lines(self) -> None:
        lines_to_clear = [row_index for row_index, row in enumerate(self.grid) if all(row)]
        for line in sorted(lines_to_clear, reverse=True):
            del self.grid[line]
            self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])

        if not lines_to_clear:
            return

        self.lines_cleared += len(lines_to_clear)
        self.score += (1, 2, 5, 10)[min(len(lines_to_clear) - 1, 3)] * 100 * self.level
        self.level = self.lines_cleared // 10 + 1
        self.fall_speed = max(0.05, 0.5 - (self.level - 1) * 0.05)

    def move(self, dx: int, dy: int) -> bool:
        if self.check_collision(self.current_piece, dx, dy):
            return False
        self.current_piece.x += dx
        self.current_piece.y += dy
        return True

    def rotate_piece(self) -> None:
        if self.current_piece.shape_index == BOMB_INDEX:
            return

        rotated_shape = self.current_piece.rotate()
        if rotated_shape is None:
            return

        original_shape = self.current_piece.shape
        self.current_piece.shape = rotated_shape

        if not self.check_collision(self.current_piece):
            return

        if not self.check_collision(self.current_piece, -1, 0):
            self.current_piece.x -= 1
        elif not self.check_collision(self.current_piece, 1, 0):
            self.current_piece.x += 1
        else:
            self.current_piece.shape = original_shape

    def update(self, dt: float) -> None:
        if self.game_over or self.paused:
            return

        if self.explosion_active:
            self.explosion_time += dt
            if self.explosion_time >= 0.5:
                self.explosion_active = False

        self.fall_time += dt
        if self.fall_time >= self.fall_speed:
            self.fall_time = 0.0
            if not self.move(0, 1):
                self.lock_piece()

        for key in [pygame.K_LEFT, pygame.K_a]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(-1, 0):
                        self.key_timers[key] = 0.0

        for key in [pygame.K_RIGHT, pygame.K_d]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(1, 0):
                        self.key_timers[key] = 0.0

        for key in [pygame.K_DOWN, pygame.K_s]:
            if self.key_states[key]:
                self.key_timers[key] += dt
                if self.key_timers[key] >= (self.key_delay if self.key_timers[key] == dt else self.key_interval):
                    if self.move(0, 1):
                        self.key_timers[key] = 0.0

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def reset(self, fonts: FontBundle) -> None:
        self.__init__(fonts)

    def draw_explosion(self, surface: pygame.Surface) -> None:
        if not self.explosion_active:
            return

        progress = min(1.0, self.explosion_time / 0.5)
        for grid_x, grid_y in self.explosion_positions:
            radius = int(GRID_SIZE * 0.7 * progress)
            center_x = GAME_AREA_X + grid_x * GRID_SIZE + GRID_SIZE // 2
            center_y = GAME_AREA_Y + grid_y * GRID_SIZE + GRID_SIZE // 2
            explosion_color = (255, max(0, int(255 * (1 - progress))), 0)
            pygame.draw.circle(surface, explosion_color, (center_x, center_y), radius)
            for angle in range(0, 360, 45):
                end_x = center_x + int(radius * 1.5 * math.cos(math.radians(angle)))
                end_y = center_y + int(radius * 1.5 * math.sin(math.radians(angle)))
                pygame.draw.line(surface, YELLOW, (center_x, center_y), (end_x, end_y), 2)

    def draw(self, surface: pygame.Surface) -> None:
        game_area = pygame.Rect(GAME_AREA_X, GAME_AREA_Y, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE)
        pygame.draw.rect(surface, BLACK, game_area)
        pygame.draw.rect(surface, WHITE, game_area, 2)

        for grid_x in range(GRID_WIDTH + 1):
            pygame.draw.line(
                surface,
                DARK_GRAY,
                (GAME_AREA_X + grid_x * GRID_SIZE, GAME_AREA_Y),
                (GAME_AREA_X + grid_x * GRID_SIZE, GAME_AREA_Y + GRID_HEIGHT * GRID_SIZE),
            )

        for grid_y in range(GRID_HEIGHT + 1):
            pygame.draw.line(
                surface,
                DARK_GRAY,
                (GAME_AREA_X, GAME_AREA_Y + grid_y * GRID_SIZE),
                (GAME_AREA_X + GRID_WIDTH * GRID_SIZE, GAME_AREA_Y + grid_y * GRID_SIZE),
            )

        for row_index, row in enumerate(self.grid):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                rect = pygame.Rect(
                    GAME_AREA_X + col_index * GRID_SIZE,
                    GAME_AREA_Y + row_index * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                )
                pygame.draw.rect(surface, cell, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)

        self.current_piece.draw(surface)
        self.draw_explosion(surface)

        sidebar = pygame.Rect(
            GAME_AREA_X + GRID_WIDTH * GRID_SIZE + 20,
            GAME_AREA_Y,
            SIDEBAR_WIDTH + 60,
            GRID_HEIGHT * GRID_SIZE,
        )
        pygame.draw.rect(surface, BLACK, sidebar)
        pygame.draw.rect(surface, WHITE, sidebar, 2)

        next_text = self.font.render("下一个:", True, WHITE)
        surface.blit(next_text, (sidebar.x + 20, sidebar.y + 20))

        next_piece_x = sidebar.x + (sidebar.width - len(self.next_piece.shape[0]) * GRID_SIZE) // 2
        next_piece_y = sidebar.y + 70
        for row_index, row in enumerate(self.next_piece.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                rect = pygame.Rect(
                    next_piece_x + col_index * GRID_SIZE,
                    next_piece_y + row_index * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                )
                pygame.draw.rect(surface, self.next_piece.color, rect)
                pygame.draw.rect(surface, WHITE, rect, 1)

                if self.next_piece.shape_index == BOMB_INDEX:
                    fuse_rect = pygame.Rect(rect.x + GRID_SIZE // 2 - 2, rect.y - 5, 4, 8)
                    pygame.draw.rect(surface, YELLOW, fuse_rect)

        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        level_text = self.font.render(f"等级: {self.level}", True, WHITE)
        lines_text = self.font.render(f"消除行: {self.lines_cleared}", True, WHITE)
        surface.blit(score_text, (sidebar.x + 20, sidebar.y + 150))
        surface.blit(level_text, (sidebar.x + 20, sidebar.y + 190))
        surface.blit(lines_text, (sidebar.x + 20, sidebar.y + 230))

        controls_y = sidebar.y + 280
        controls = [
            "操作说明:",
            "←/A →/D : 左右移动",
            "↑/W : 旋转",
            "↓/S : 加速下落",
            "空格 : 直接落下",
            "P : 暂停/继续",
            "R : 重新开始",
            "",
            "特殊方块:",
            "炸弹 - 清除周围",
            "方块 (不计分)",
        ]
        for index, text in enumerate(controls):
            control_text = self.small_font.render(text, True, WHITE)
            surface.blit(control_text, (sidebar.x + 20, controls_y + index * 30))

        if self.paused:
            pause_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_surface.fill((0, 0, 0, 128))
            surface.blit(pause_surface, (0, 0))

            pause_text = self.big_font.render("游戏暂停", True, YELLOW)
            text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(pause_text, text_rect)

            continue_text = self.font.render("按P键继续", True, WHITE)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            surface.blit(continue_text, continue_rect)

        if self.game_over:
            game_over_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            game_over_surface.fill((0, 0, 0, 192))
            surface.blit(game_over_surface, (0, 0))

            game_over_text = self.big_font.render("游戏结束!", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(game_over_text, text_rect)

            score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            surface.blit(score_text, score_rect)

            restart_text = self.font.render("按R键重新开始", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            surface.blit(restart_text, restart_rect)


def main(max_frames: int | None = None) -> int:
    screen = initialize_runtime((SCREEN_WIDTH, SCREEN_HEIGHT), WINDOW_CAPTION)
    fonts = create_font_bundle()
    game = Game(fonts)
    clock = pygame.time.Clock()
    frame_count = 0
    running = True

    try:
        while running:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game.reset(fonts)
                    if event.key == pygame.K_p:
                        game.toggle_pause()
                    if event.key in game.key_states:
                        game.key_states[event.key] = True
                        game.key_timers[event.key] = 0.0
                    if not game.paused and not game.game_over:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            game.rotate_piece()
                        elif event.key == pygame.K_SPACE:
                            while game.move(0, 1):
                                pass
                            game.lock_piece()
                elif event.type == pygame.KEYUP and event.key in game.key_states:
                    game.key_states[event.key] = False
                    game.key_timers[event.key] = 0.0

            game.update(dt)

            screen.fill(BACKGROUND_COLOR)
            title_text = game.big_font.render("俄罗斯方块", True, YELLOW)
            title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            screen.blit(title_text, title_rect)

            game.draw(screen)
            pygame.display.flip()

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        shutdown_runtime()

    return 0
