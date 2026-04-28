import os
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from tetris_app.game_state import GameState
from tetris_app.pieces import PIECE_COLORS, Tetromino


@pytest.fixture
def state():
    current_piece = Tetromino(
        shape_index=0,
        shape=[[1]],
        color=PIECE_COLORS[0],
        x=4,
        y=3,
    )
    state = GameState()
    state.current_piece = current_piece
    yield state


@pytest.mark.parametrize(
    ("action", "axis", "delta"),
    [
        ("left", "x", -1),
        ("right", "x", 1),
        ("down", "y", 1),
    ],
)
def test_held_keys_wait_for_initial_delay_before_first_repeat(state, action, axis, delta):
    start = getattr(state.current_piece, axis)

    state.set_hold(action, True)
    state.update(0.10)
    state.update(0.04)
    assert getattr(state.current_piece, axis) == start

    state.update(0.01)
    assert getattr(state.current_piece, axis) == start + delta


@pytest.mark.parametrize(
    ("action", "axis", "delta"),
    [
        ("left", "x", -1),
        ("right", "x", 1),
        ("down", "y", 1),
    ],
)
def test_held_keys_repeat_on_interval_after_first_repeat(state, action, axis, delta):
    start = getattr(state.current_piece, axis)

    state.set_hold(action, True)
    state.update(state.key_delay)
    assert getattr(state.current_piece, axis) == start + delta

    state.update(0.04)
    assert getattr(state.current_piece, axis) == start + delta

    state.update(0.01)
    assert getattr(state.current_piece, axis) == start + (delta * 2)


def test_releasing_a_key_resets_repeat_state(state):
    start = state.current_piece.x

    state.set_hold("left", True)
    state.update(state.key_delay)
    assert state.current_piece.x == start - 1

    state.set_hold("left", False)
    state.set_hold("left", True)
    state.update(0.14)
    assert state.current_piece.x == start - 1

    state.update(0.01)
    assert state.current_piece.x == start - 2


@pytest.mark.parametrize(
    ("action", "axis", "delta"),
    [
        ("left", "x", -1),
        ("right", "x", 1),
        ("down", "y", 1),
    ],
)
def test_press_action_moves_immediately_and_starts_hold_tracking(state, action, axis, delta):
    start = getattr(state.current_piece, axis)

    moved = state.press_action(action)

    assert moved
    assert getattr(state.current_piece, axis) == start + delta
    assert state.repeat_trackers[action].held


def test_held_repeat_consumes_large_elapsed_frame_without_missing_steps(state):
    start = state.current_piece.x

    state.set_hold("right", True)
    state.update(state.key_delay + (state.key_interval * 2))

    assert state.current_piece.x == start + 3
