import os
import random
import sys
from pathlib import Path

import pygame


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from tetris_app.game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from tetris_app.layout import build_layout
from tetris_app.renderers import GameRenderer
from tetris_app.resources import FontBundle
from tetris_app.theme import build_theme


def test_renderer_builds_cached_surfaces_under_headless_pygame():
    pygame.init()
    try:
        surface = pygame.Surface((800, 600), pygame.SRCALPHA)
        fonts = FontBundle(
            body=pygame.font.Font(None, 36),
            small=pygame.font.Font(None, 24),
            title=pygame.font.Font(None, 64),
        )
        layout = build_layout(
            screen_width=800,
            screen_height=600,
            grid_size=30,
            grid_width=GRID_WIDTH,
            grid_height=GRID_HEIGHT,
            sidebar_width=220,
        )
        renderer = GameRenderer(theme=build_theme(), layout=layout, grid_size=30)
        state = GameState(random.Random(0))

        renderer.draw_frame(surface, state, fonts)
        cached_chrome = renderer._chrome_surface
        cached_paused_overlay = renderer._overlay_surfaces["paused"]

        state.paused = True
        renderer.draw_frame(surface, state, fonts)

        assert cached_chrome is renderer._chrome_surface
        assert cached_paused_overlay is renderer._overlay_surfaces["paused"]
        assert renderer._static_text_cache
        assert surface.get_width() == 800
    finally:
        pygame.quit()
