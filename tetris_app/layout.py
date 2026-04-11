from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class GameLayout:
    screen: pygame.Rect
    board: pygame.Rect
    sidebar: pygame.Rect
    title_badge: pygame.Rect
    preview_card: pygame.Rect
    stats_card: pygame.Rect
    controls_card: pygame.Rect
    overlay_card: pygame.Rect


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
    sidebar_width = max(sidebar_width, 240)
    board_x = 44
    board_y = 0
    sidebar_x = board_x + board_width + 30
    sidebar_y = 74
    sidebar_height = screen_height - 108

    board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
    sidebar_rect = pygame.Rect(sidebar_x, sidebar_y, sidebar_width, sidebar_height)
    preview_card = pygame.Rect(sidebar_rect.x, sidebar_rect.y, sidebar_rect.width, 132)
    stats_card = pygame.Rect(sidebar_rect.x, preview_card.bottom + 16, sidebar_rect.width, 136)
    controls_card = pygame.Rect(
        sidebar_rect.x,
        stats_card.bottom + 16,
        sidebar_rect.width,
        sidebar_rect.bottom - (stats_card.bottom + 16),
    )
    return GameLayout(
        screen=pygame.Rect(0, 0, screen_width, screen_height),
        board=board_rect,
        sidebar=sidebar_rect,
        title_badge=pygame.Rect(24, 18, screen_width - 48, 56),
        preview_card=preview_card,
        stats_card=stats_card,
        controls_card=controls_card,
        overlay_card=pygame.Rect(screen_width // 2 - 214, screen_height // 2 - 132, 428, 264),
    )
