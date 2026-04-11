from __future__ import annotations

from dataclasses import dataclass
import random


Color = tuple[int, int, int]

PIECE_SHAPES = (
    ((1, 1, 1, 1),),
    ((1, 1), (1, 1)),
    ((0, 1, 0), (1, 1, 1)),
    ((1, 0, 0), (1, 1, 1)),
    ((0, 0, 1), (1, 1, 1)),
    ((0, 1, 1), (1, 1, 0)),
    ((1, 1, 0), (0, 1, 1)),
    ((1,),),
)

PIECE_COLORS: tuple[Color, ...] = (
    (0, 255, 255),
    (255, 255, 0),
    (180, 0, 255),
    (255, 165, 0),
    (0, 120, 255),
    (0, 255, 0),
    (255, 0, 0),
    (255, 100, 0),
)

BOMB_INDEX = 7
BOMB_PROBABILITY = 1 / 15


def clone_shape(shape: tuple[tuple[int, ...], ...] | list[list[int]]) -> list[list[int]]:
    return [list(row) for row in shape]


def rotate_shape(shape: list[list[int]]) -> list[list[int]]:
    rows = len(shape)
    cols = len(shape[0])
    rotated = [[0 for _ in range(rows)] for _ in range(cols)]
    for row_index in range(rows):
        for col_index in range(cols):
            rotated[col_index][rows - 1 - row_index] = shape[row_index][col_index]
    return rotated


@dataclass(slots=True)
class Tetromino:
    shape_index: int
    shape: list[list[int]]
    color: Color
    x: int
    y: int

    @classmethod
    def spawn(cls, grid_width: int, rng: random.Random) -> "Tetromino":
        if rng.random() < BOMB_PROBABILITY:
            shape_index = BOMB_INDEX
        else:
            shape_index = rng.randint(0, BOMB_INDEX - 1)

        shape = clone_shape(PIECE_SHAPES[shape_index])
        if shape_index == BOMB_INDEX:
            x = grid_width // 2
        else:
            x = grid_width // 2 - len(shape[0]) // 2

        return cls(
            shape_index=shape_index,
            shape=shape,
            color=PIECE_COLORS[shape_index],
            x=x,
            y=0,
        )

    def rotated_shape(self) -> list[list[int]] | None:
        if self.shape_index == BOMB_INDEX:
            return None
        return rotate_shape(self.shape)

    def clone(self) -> "Tetromino":
        return Tetromino(
            shape_index=self.shape_index,
            shape=clone_shape(self.shape),
            color=self.color,
            x=self.x,
            y=self.y,
        )
