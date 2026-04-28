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
)

PIECE_COLORS: tuple[Color, ...] = (
    (214, 178, 127),
    (230, 196, 132),
    (198, 156, 116),
    (185, 133, 89),
    (171, 127, 92),
    (206, 166, 114),
    (160, 108, 79),
)


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
        shape_index = rng.randint(0, len(PIECE_SHAPES) - 1)
        shape = clone_shape(PIECE_SHAPES[shape_index])
        x = grid_width // 2 - len(shape[0]) // 2

        return cls(
            shape_index=shape_index,
            shape=shape,
            color=PIECE_COLORS[shape_index],
            x=x,
            y=0,
        )

    def rotated_shape(self) -> list[list[int]]:
        return rotate_shape(self.shape)

    def clone(self) -> "Tetromino":
        return Tetromino(
            shape_index=self.shape_index,
            shape=clone_shape(self.shape),
            color=self.color,
            x=self.x,
            y=self.y,
        )
