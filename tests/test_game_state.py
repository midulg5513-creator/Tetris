import random

from tetris_app.game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from tetris_app.pieces import PIECE_COLORS, Tetromino


def make_piece(shape_index: int = 0, x: int = 0, y: int = 0) -> Tetromino:
    return Tetromino(
        shape_index=shape_index,
        shape=[[1]],
        color=PIECE_COLORS[shape_index],
        x=x,
        y=y,
    )


def test_clear_lines_updates_score_and_level_progression():
    state = GameState(random.Random(0))
    state.grid[-1] = [PIECE_COLORS[0] for _ in range(GRID_WIDTH)]
    state.grid[-2] = [PIECE_COLORS[1] for _ in range(GRID_WIDTH)]

    state.clear_lines()

    assert state.lines_cleared == 2
    assert state.score == 200
    assert state.level == 1
    assert all(cell is None for cell in state.grid[0])
    assert all(cell is None for cell in state.grid[1])


def test_collision_checks_board_edges():
    state = GameState(random.Random(0))

    left_edge_piece = make_piece(x=0, y=0)
    right_edge_piece = make_piece(x=GRID_WIDTH - 1, y=0)
    floor_piece = make_piece(x=0, y=GRID_HEIGHT - 1)

    assert state.check_collision(left_edge_piece, dx=-1)
    assert state.check_collision(right_edge_piece, dx=1)
    assert state.check_collision(floor_piece, dy=1)


def test_bomb_explosion_clears_surrounding_cells_only():
    state = GameState(random.Random(0))
    center_x = 5
    center_y = 5

    for grid_y in range(center_y - 1, center_y + 2):
        for grid_x in range(center_x - 1, center_x + 2):
            state.grid[grid_y][grid_x] = PIECE_COLORS[0]

    state.explode_bomb(center_x, center_y)

    for grid_y in range(center_y - 1, center_y + 2):
        for grid_x in range(center_x - 1, center_x + 2):
            if grid_x == center_x and grid_y == center_y:
                assert state.grid[grid_y][grid_x] == PIECE_COLORS[0]
            else:
                assert state.grid[grid_y][grid_x] is None


def test_reset_restores_core_runtime_state():
    state = GameState(random.Random(0))
    state.score = 900
    state.level = 4
    state.lines_cleared = 12
    state.game_over = True
    state.paused = True
    state.grid[-1][0] = PIECE_COLORS[0]

    state.reset()

    assert state.score == 0
    assert state.level == 1
    assert state.lines_cleared == 0
    assert not state.game_over
    assert not state.paused
    assert all(cell is None for row in state.grid for cell in row)
