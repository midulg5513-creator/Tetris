import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from tetris_app import app
from tetris_app.resources import FontBundle


@pytest.fixture
def game():
    app.pygame.font.init()
    fonts = FontBundle(
        body=app.pygame.font.Font(None, 36),
        small=app.pygame.font.Font(None, 24),
        title=app.pygame.font.Font(None, 64),
    )
    state = app.Game(fonts)
    state.current_piece.shape = [[1]]
    state.current_piece.shape_index = 0
    state.current_piece.x = 4
    state.current_piece.y = 3
    yield state
    app.pygame.quit()


@pytest.mark.parametrize(
    ("key", "axis", "delta"),
    [
        (app.pygame.K_LEFT, "x", -1),
        (app.pygame.K_RIGHT, "x", 1),
        (app.pygame.K_DOWN, "y", 1),
    ],
)
def test_held_keys_wait_for_initial_delay_before_first_repeat(game, key, axis, delta):
    start = getattr(game.current_piece, axis)

    game.set_key_state(key, True)
    game.update(0.10)
    game.update(0.04)
    assert getattr(game.current_piece, axis) == start

    game.update(0.01)
    assert getattr(game.current_piece, axis) == start + delta


@pytest.mark.parametrize(
    ("key", "axis", "delta"),
    [
        (app.pygame.K_LEFT, "x", -1),
        (app.pygame.K_RIGHT, "x", 1),
        (app.pygame.K_DOWN, "y", 1),
    ],
)
def test_held_keys_repeat_on_interval_after_first_repeat(game, key, axis, delta):
    start = getattr(game.current_piece, axis)

    game.set_key_state(key, True)
    game.update(game.key_delay)
    assert getattr(game.current_piece, axis) == start + delta

    game.update(0.04)
    assert getattr(game.current_piece, axis) == start + delta

    game.update(0.01)
    assert getattr(game.current_piece, axis) == start + (delta * 2)


def test_releasing_a_key_resets_repeat_state(game):
    start = game.current_piece.x

    game.set_key_state(app.pygame.K_LEFT, True)
    game.update(game.key_delay)
    assert game.current_piece.x == start - 1

    game.set_key_state(app.pygame.K_LEFT, False)
    game.set_key_state(app.pygame.K_LEFT, True)
    game.update(0.14)
    assert game.current_piece.x == start - 1

    game.update(0.01)
    assert game.current_piece.x == start - 2
