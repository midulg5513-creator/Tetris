from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class GameLayout:
    screen: pygame.Rect
    board: pygame.Rect
    sidebar: pygame.Rect
    title_center: tuple[int, int]
    preview_origin: tuple[int, int]
    stats_origin: tuple[int, int]
    controls_origin: tuple[int, int]


def build_layout(
    screen_width: int,
    screen_height: int,
    grid_size: int,
    grid_width: int,
    grid_height: int,
    sidebar_width: int,
) -> GameLayout:
    board_width = grid_width * grid_size
    board_height = grid_height * grid_size
    board_x = (screen_width - sidebar_width - board_width) // 2
    board_y = (screen_height - board_height) // 2
    sidebar_x = board_x + board_width + 24
    sidebar_y = board_y
    sidebar_height = board_height

    board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
    sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_width, sidebar_height)
    return GameLayout(
        screen=pygame.Rect(0, 0, screen_width, screen_height),
        board=board_rect,
        sidebar=sidebar_rect,
        title_center=(screen_width // 2, 34),
        preview_origin=(sidebar_rect.x + 48, sidebar_rect.y + 72),
        stats_origin=(sidebar_rect.x + 18, sidebar_rect.y + 164),
        controls_origin=(sidebar_rect.x + 18, sidebar_rect.y + 304),
    )
