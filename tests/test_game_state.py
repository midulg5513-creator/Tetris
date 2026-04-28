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
    anchor_row = [None for _ in range(GRID_WIDTH)]
    anchor_row[0] = PIECE_COLORS[2]
    state.grid[-3] = anchor_row
    state.grid[-1] = [PIECE_COLORS[0] for _ in range(GRID_WIDTH)]
    state.grid[-2] = [PIECE_COLORS[1] for _ in range(GRID_WIDTH)]

    state.clear_lines()

    assert state.lines_cleared == 2
    assert state.score == 200
    assert state.level == 1
    assert all(cell is None for cell in state.grid[0])
    assert all(cell is None for cell in state.grid[1])
    assert state.grid[-1] == anchor_row
    assert not any(all(row) for row in state.grid)


def test_collision_checks_board_edges():
    state = GameState(random.Random(0))

    left_edge_piece = make_piece(x=0, y=0)
    right_edge_piece = make_piece(x=GRID_WIDTH - 1, y=0)
    floor_piece = make_piece(x=0, y=GRID_HEIGHT - 1)

    assert state.check_collision(left_edge_piece, dx=-1)
    assert state.check_collision(right_edge_piece, dx=1)
    assert state.check_collision(floor_piece, dy=1)


def test_spawned_pieces_are_standard_tetrominoes_only():
    random_source = random.Random(0)
    state = GameState(random_source)

    shape_indexes = {state.current_piece.shape_index, state.next_piece.shape_index}
    for _ in range(64):
        state.new_piece()
        shape_indexes.add(state.current_piece.shape_index)
        shape_indexes.add(state.next_piece.shape_index)

    assert shape_indexes == set(range(len(PIECE_COLORS)))


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
