from __future__ import annotations

import math

import pygame

from .game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from .layout import GameLayout
from .pieces import BOMB_INDEX, Tetromino
from .resources import FontBundle
from .theme import Theme


class GameRenderer:
    def __init__(self, theme: Theme, layout: GameLayout, grid_size: int) -> None:
        self.theme = theme
        self.layout = layout
        self.grid_size = grid_size

    def draw_frame(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        surface.fill(self.theme.background_color)
        title = fonts.title.render("TETRIS", True, self.theme.accent)
        surface.blit(title, title.get_rect(center=self.layout.title_center))
        self.draw_board(surface, state)
        self.draw_sidebar(surface, state, fonts)
        self.draw_overlay(surface, state, fonts)

    def draw_block(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        pygame.draw.rect(surface, color, rect, border_radius=self.theme.block_radius)
        pygame.draw.rect(surface, self.theme.panel_border, rect, 1, border_radius=self.theme.block_radius)
        highlight = rect.inflate(-6, -6)
        pygame.draw.rect(
            surface,
            tuple(min(255, channel + self.theme.highlight_boost) for channel in color),
            highlight,
            1,
            border_radius=max(1, self.theme.block_radius - 1),
        )

    def draw_piece(
        self,
        surface: pygame.Surface,
        piece: Tetromino,
        origin: tuple[int, int],
        *,
        board_positioned: bool = True,
    ) -> None:
        origin_x, origin_y = origin
        for row_index, row in enumerate(piece.shape):
            for col_index, cell in enumerate(row):
                if not cell:
                    continue

                grid_x = piece.x + col_index if board_positioned else col_index
                grid_y = piece.y + row_index if board_positioned else row_index
                rect = pygame.Rect(
                    origin_x + grid_x * self.grid_size,
                    origin_y + grid_y * self.grid_size,
                    self.grid_size,
                    self.grid_size,
                )
                self.draw_block(surface, rect, piece.color)
                if piece.shape_index != BOMB_INDEX:
                    continue

                fuse_rect = pygame.Rect(rect.centerx - 2, rect.y - 6, 4, 9)
                pygame.draw.rect(surface, self.theme.fuse, fuse_rect, border_radius=2)
                pygame.draw.circle(surface, self.theme.panel_border, (rect.centerx, rect.y - 8), 3)

    def draw_explosion(self, surface: pygame.Surface, state: GameState) -> None:
        if not state.explosion_active:
            return

        progress = min(1.0, state.explosion_time / 0.5)
        for grid_x, grid_y in state.explosion_positions:
            center_x = self.layout.board.x + grid_x * self.grid_size + self.grid_size // 2
            center_y = self.layout.board.y + grid_y * self.grid_size + self.grid_size // 2
            radius = int(self.grid_size * 0.7 * progress)
            explosion_color = (255, max(0, int(255 * (1 - progress))), 0)
            pygame.draw.circle(surface, explosion_color, (center_x, center_y), radius)
            for angle in range(0, 360, 45):
                end_x = center_x + int(radius * 1.4 * math.cos(math.radians(angle)))
                end_y = center_y + int(radius * 1.4 * math.sin(math.radians(angle)))
                pygame.draw.line(surface, self.theme.fuse, (center_x, center_y), (end_x, end_y), 2)

    def draw_board(self, surface: pygame.Surface, state: GameState) -> None:
        pygame.draw.rect(surface, self.theme.panel_background, self.layout.board, border_radius=self.theme.panel_radius)
        pygame.draw.rect(surface, self.theme.panel_border, self.layout.board, 2, border_radius=self.theme.panel_radius)

        for grid_x in range(GRID_WIDTH + 1):
            start = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.y)
            end = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.y + self.layout.board.height)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

        for grid_y in range(GRID_HEIGHT + 1):
            start = (self.layout.board.x, self.layout.board.y + grid_y * self.grid_size)
            end = (self.layout.board.x + self.layout.board.width, self.layout.board.y + grid_y * self.grid_size)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

        for row_index, row in enumerate(state.grid):
            for col_index, cell in enumerate(row):
                if cell is None:
                    continue
                rect = pygame.Rect(
                    self.layout.board.x + col_index * self.grid_size,
                    self.layout.board.y + row_index * self.grid_size,
                    self.grid_size,
                    self.grid_size,
                )
                self.draw_block(surface, rect, cell)

        self.draw_piece(surface, state.current_piece, self.layout.board.topleft)
        self.draw_explosion(surface, state)

    def draw_sidebar(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        pygame.draw.rect(surface, self.theme.panel_background, self.layout.sidebar, border_radius=self.theme.panel_radius)
        pygame.draw.rect(surface, self.theme.panel_border, self.layout.sidebar, 2, border_radius=self.theme.panel_radius)

        next_label = fonts.body.render("Next", True, self.theme.text)
        surface.blit(next_label, (self.layout.sidebar.x + 18, self.layout.sidebar.y + 18))
        self.draw_piece(surface, state.next_piece, self.layout.preview_origin, board_positioned=False)

        stats = [
            f"Score  {state.score}",
            f"Level  {state.level}",
            f"Lines  {state.lines_cleared}",
        ]
        for index, text in enumerate(stats):
            label = fonts.body.render(text, True, self.theme.text)
            surface.blit(label, (self.layout.stats_origin[0], self.layout.stats_origin[1] + index * 40))

        controls = [
            "Controls",
            "A / D  Move",
            "W      Rotate",
            "S      Soft Drop",
            "Space  Hard Drop",
            "P      Pause",
            "R      Restart",
            "",
            "Bomb blocks clear",
            "the 8 surrounding cells.",
        ]
        for index, text in enumerate(controls):
            label = fonts.small.render(text, True, self.theme.text)
            surface.blit(label, (self.layout.controls_origin[0], self.layout.controls_origin[1] + index * 24))

    def draw_overlay(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        if state.paused:
            overlay = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            title = fonts.title.render("Paused", True, self.theme.accent)
            body = fonts.body.render("Press P to resume", True, self.theme.text)
            surface.blit(title, title.get_rect(center=(self.layout.screen.centerx, self.layout.screen.centery - 36)))
            surface.blit(body, body.get_rect(center=(self.layout.screen.centerx, self.layout.screen.centery + 18)))

        if state.game_over:
            overlay = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
            title = fonts.title.render("Game Over", True, self.theme.danger)
            score = fonts.body.render(f"Final Score  {state.score}", True, self.theme.text)
            restart = fonts.body.render("Press R to restart", True, self.theme.text)
            surface.blit(title, title.get_rect(center=(self.layout.screen.centerx, self.layout.screen.centery - 52)))
            surface.blit(score, score.get_rect(center=(self.layout.screen.centerx, self.layout.screen.centery + 4)))
            surface.blit(restart, restart.get_rect(center=(self.layout.screen.centerx, self.layout.screen.centery + 48)))
