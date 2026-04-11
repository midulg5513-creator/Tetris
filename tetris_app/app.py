from __future__ import annotations

import math

import pygame

from .game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from .pieces import BOMB_INDEX, Tetromino
from .resources import FontBundle, create_font_bundle, initialize_runtime, shutdown_runtime


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 30
SIDEBAR_WIDTH = 220
BOARD_WIDTH = GRID_WIDTH * GRID_SIZE
BOARD_HEIGHT = GRID_HEIGHT * GRID_SIZE
BOARD_X = (SCREEN_WIDTH - SIDEBAR_WIDTH - BOARD_WIDTH) // 2
BOARD_Y = (SCREEN_HEIGHT - BOARD_HEIGHT) // 2
SIDEBAR_X = BOARD_X + BOARD_WIDTH + 24
SIDEBAR_Y = BOARD_Y
WINDOW_CAPTION = "Neon Tetris"

BACKGROUND_COLOR = (40, 40, 60)
PANEL_BACKGROUND = (12, 16, 28)
GRID_LINE_COLOR = (46, 58, 82)
TEXT_COLOR = (235, 242, 255)
ACCENT_COLOR = (255, 230, 120)
RED = (255, 84, 112)
WHITE = (255, 255, 255)
YELLOW = (255, 224, 90)

KEY_TO_ACTION = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
}


def draw_block(surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, WHITE, rect, 1, border_radius=6)
    highlight = rect.inflate(-6, -6)
    pygame.draw.rect(
        surface,
        tuple(min(255, channel + 50) for channel in color),
        highlight,
        1,
        border_radius=5,
    )


def draw_piece(
    surface: pygame.Surface,
    piece: Tetromino,
    origin_x: int,
    origin_y: int,
    cell_size: int = GRID_SIZE,
    board_positioned: bool = True,
) -> None:
    for row_index, row in enumerate(piece.shape):
        for col_index, cell in enumerate(row):
            if not cell:
                continue

            grid_x = piece.x + col_index if board_positioned else col_index
            grid_y = piece.y + row_index if board_positioned else row_index
            rect = pygame.Rect(
                origin_x + grid_x * cell_size,
                origin_y + grid_y * cell_size,
                cell_size,
                cell_size,
            )

            draw_block(surface, rect, piece.color)
            if piece.shape_index != BOMB_INDEX:
                continue

            fuse_rect = pygame.Rect(rect.centerx - 2, rect.y - 6, 4, 9)
            pygame.draw.rect(surface, YELLOW, fuse_rect, border_radius=2)
            pygame.draw.circle(surface, WHITE, (rect.centerx, rect.y - 8), 3)


def draw_explosion(surface: pygame.Surface, state: GameState) -> None:
    if not state.explosion_active:
        return

    progress = min(1.0, state.explosion_time / 0.5)
    for grid_x, grid_y in state.explosion_positions:
        center_x = BOARD_X + grid_x * GRID_SIZE + GRID_SIZE // 2
        center_y = BOARD_Y + grid_y * GRID_SIZE + GRID_SIZE // 2
        radius = int(GRID_SIZE * 0.7 * progress)
        explosion_color = (255, max(0, int(255 * (1 - progress))), 0)
        pygame.draw.circle(surface, explosion_color, (center_x, center_y), radius)
        for angle in range(0, 360, 45):
            end_x = center_x + int(radius * 1.4 * math.cos(math.radians(angle)))
            end_y = center_y + int(radius * 1.4 * math.sin(math.radians(angle)))
            pygame.draw.line(surface, YELLOW, (center_x, center_y), (end_x, end_y), 2)


def draw_board(surface: pygame.Surface, state: GameState) -> None:
    board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(surface, PANEL_BACKGROUND, board_rect, border_radius=16)
    pygame.draw.rect(surface, WHITE, board_rect, 2, border_radius=16)

    for grid_x in range(GRID_WIDTH + 1):
        start = (BOARD_X + grid_x * GRID_SIZE, BOARD_Y)
        end = (BOARD_X + grid_x * GRID_SIZE, BOARD_Y + BOARD_HEIGHT)
        pygame.draw.line(surface, GRID_LINE_COLOR, start, end)

    for grid_y in range(GRID_HEIGHT + 1):
        start = (BOARD_X, BOARD_Y + grid_y * GRID_SIZE)
        end = (BOARD_X + BOARD_WIDTH, BOARD_Y + grid_y * GRID_SIZE)
        pygame.draw.line(surface, GRID_LINE_COLOR, start, end)

    for row_index, row in enumerate(state.grid):
        for col_index, cell in enumerate(row):
            if cell is None:
                continue

            rect = pygame.Rect(
                BOARD_X + col_index * GRID_SIZE,
                BOARD_Y + row_index * GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE,
            )
            draw_block(surface, rect, cell)

    draw_piece(surface, state.current_piece, BOARD_X, BOARD_Y)
    draw_explosion(surface, state)


def draw_sidebar(surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
    sidebar_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(surface, PANEL_BACKGROUND, sidebar_rect, border_radius=16)
    pygame.draw.rect(surface, WHITE, sidebar_rect, 2, border_radius=16)

    next_label = fonts.body.render("Next", True, TEXT_COLOR)
    surface.blit(next_label, (sidebar_rect.x + 18, sidebar_rect.y + 18))

    preview_origin_x = sidebar_rect.x + 48
    preview_origin_y = sidebar_rect.y + 72
    draw_piece(surface, state.next_piece, preview_origin_x, preview_origin_y, board_positioned=False)

    stats = [
        f"Score  {state.score}",
        f"Level  {state.level}",
        f"Lines  {state.lines_cleared}",
    ]
    for index, text in enumerate(stats):
        label = fonts.body.render(text, True, TEXT_COLOR)
        surface.blit(label, (sidebar_rect.x + 18, sidebar_rect.y + 164 + index * 40))

    controls = [
        "Controls",
        "A / D  Move",
        "W      Rotate",
        "S      Soft Drop",
        "Space  Hard Drop",
        "P      Pause",
        "R      Restart",
        "",
        "Bomb blocks clear",
        "the 8 surrounding cells.",
    ]
    for index, text in enumerate(controls):
        label = fonts.small.render(text, True, TEXT_COLOR)
        surface.blit(label, (sidebar_rect.x + 18, sidebar_rect.y + 304 + index * 24))


def draw_overlay(surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
    if state.paused:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title = fonts.title.render("Paused", True, ACCENT_COLOR)
        body = fonts.body.render("Press P to resume", True, TEXT_COLOR)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 36)))
        surface.blit(body, body.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 18)))

    if state.game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        title = fonts.title.render("Game Over", True, RED)
        score = fonts.body.render(f"Final Score  {state.score}", True, TEXT_COLOR)
        restart = fonts.body.render("Press R to restart", True, TEXT_COLOR)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 52)))
        surface.blit(score, score.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 4)))
        surface.blit(restart, restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 48)))


def draw_frame(surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
    surface.fill(BACKGROUND_COLOR)
    title = fonts.title.render("TETRIS", True, ACCENT_COLOR)
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 34)))
    draw_board(surface, state)
    draw_sidebar(surface, state, fonts)
    draw_overlay(surface, state, fonts)


def main(max_frames: int | None = None) -> int:
    screen = initialize_runtime((SCREEN_WIDTH, SCREEN_HEIGHT), WINDOW_CAPTION)
    fonts = create_font_bundle()
    state = GameState()
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
                        state.reset()
                    elif event.key == pygame.K_p:
                        state.toggle_pause()
                    elif event.key in KEY_TO_ACTION:
                        state.set_hold(KEY_TO_ACTION[event.key], True)
                    elif not state.paused and not state.game_over and event.key in (pygame.K_UP, pygame.K_w):
                        state.rotate_current()
                    elif not state.paused and not state.game_over and event.key == pygame.K_SPACE:
                        state.hard_drop()
                elif event.type == pygame.KEYUP and event.key in KEY_TO_ACTION:
                    state.set_hold(KEY_TO_ACTION[event.key], False)

            state.update(dt)
            draw_frame(screen, state, fonts)
            pygame.display.flip()

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        shutdown_runtime()

    return 0
