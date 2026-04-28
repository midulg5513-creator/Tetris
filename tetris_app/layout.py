from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True, slots=True)
class GameLayout:
    screen: pygame.Rect
    cabinet: pygame.Rect
    machine_head: pygame.Rect
    score_track: pygame.Rect
    board_frame: pygame.Rect
    board: pygame.Rect
    sidebar: pygame.Rect
    title_area: pygame.Rect
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
    frame_margin = 12
    frame_gap = 26
    board_frame_width = board_width + frame_margin * 2
    board_frame_height = board_height + frame_margin * 2
    cluster_width = board_frame_width + frame_gap + sidebar_width
    cluster_x = max(38, (screen_width - cluster_width) // 2)

    board_frame = pygame.Rect(cluster_x, 48, board_frame_width, board_frame_height)
    board_rect = pygame.Rect(
        board_frame.x + frame_margin,
        board_frame.y + frame_margin,
        board_width,
        board_height,
    )
    machine_head = pygame.Rect(board_frame.x + 8, 18, board_frame.width - 16, 36)
    score_track = pygame.Rect(machine_head.x + 92, machine_head.y + 8, machine_head.width - 108, 16)

    available_sidebar_width = max(210, screen_width - board_frame.right - frame_gap - cluster_x)
    sidebar_rect = pygame.Rect(
        board_frame.right + frame_gap,
        board_frame.y + 16,
        min(max(sidebar_width, 220), available_sidebar_width),
        board_frame.height - 16,
    )

    preview_card = pygame.Rect(sidebar_rect.x + 14, sidebar_rect.y + 18, sidebar_rect.width - 28, 116)
    stats_card = pygame.Rect(sidebar_rect.x + 14, preview_card.bottom + 14, sidebar_rect.width - 28, 144)
    controls_card = pygame.Rect(
        sidebar_rect.x + 14,
        stats_card.bottom + 14,
        sidebar_rect.width - 28,
        sidebar_rect.bottom - 18 - (stats_card.bottom + 14),
    )
    cabinet = pygame.Rect(cluster_x - 22, 10, cluster_width + 44, screen_height - 22)

    return GameLayout(
        screen=pygame.Rect(0, 0, screen_width, screen_height),
        cabinet=cabinet,
        machine_head=machine_head,
        score_track=score_track,
        board_frame=board_frame,
        board=board_rect,
        sidebar=sidebar_rect,
        title_area=pygame.Rect(machine_head.x, machine_head.y, machine_head.width, machine_head.height),
        preview_card=preview_card,
        stats_card=stats_card,
        controls_card=controls_card,
        overlay_card=pygame.Rect(screen_width // 2 - 182, screen_height // 2 - 102, 364, 204),
    )
