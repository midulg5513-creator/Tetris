from __future__ import annotations

import pygame

from .game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from .layout import build_layout
from .renderers import GameRenderer
from .resources import create_font_bundle, initialize_runtime, shutdown_runtime
from .theme import build_theme


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 26
SIDEBAR_WIDTH = 236
WINDOW_CAPTION = "Wooden Tetris"

KEY_TO_ACTION = {
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
}


def main(max_frames: int | None = None) -> int:
    screen = initialize_runtime((SCREEN_WIDTH, SCREEN_HEIGHT), WINDOW_CAPTION)
    fonts = create_font_bundle()
    theme = build_theme()
    layout = build_layout(
        screen_width=SCREEN_WIDTH,
        screen_height=SCREEN_HEIGHT,
        grid_size=GRID_SIZE,
        grid_width=GRID_WIDTH,
        grid_height=GRID_HEIGHT,
        sidebar_width=SIDEBAR_WIDTH,
    )
    renderer = GameRenderer(theme=theme, layout=layout, grid_size=GRID_SIZE)
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
                        state.press_action(KEY_TO_ACTION[event.key])
                    elif not state.paused and not state.game_over and event.key in (pygame.K_UP, pygame.K_w):
                        state.rotate_current()
                    elif not state.paused and not state.game_over and event.key == pygame.K_SPACE:
                        state.hard_drop()
                elif event.type == pygame.KEYUP and event.key in KEY_TO_ACTION:
                    state.set_hold(KEY_TO_ACTION[event.key], False)

            state.update(dt)
            renderer.draw_frame(screen, state, fonts)
            pygame.display.flip()

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False
    finally:
        shutdown_runtime()

    return 0
