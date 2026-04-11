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
        self._chrome_surface: pygame.Surface | None = None
        self._overlay_surfaces: dict[str, pygame.Surface] = {}
        self._font_cache_key: tuple[int, int, int] | None = None
        self._static_text_cache: dict[str, pygame.Surface] = {}
        self._dynamic_text_cache: dict[tuple[str, str], pygame.Surface] = {}

    def draw_frame(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        self._ensure_caches(fonts)
        assert self._chrome_surface is not None
        surface.blit(self._chrome_surface, (0, 0))
        self._draw_title(surface, fonts)
        self.draw_board(surface, state)
        self.draw_sidebar(surface, state, fonts)
        self.draw_overlay(surface, state, fonts)

    def _ensure_caches(self, fonts: FontBundle) -> None:
        if self._chrome_surface is None:
            self._chrome_surface = self._build_chrome_surface()
            self._overlay_surfaces = self._build_overlay_surfaces()

        font_key = (id(fonts.body), id(fonts.small), id(fonts.title))
        if self._font_cache_key == font_key:
            return

        self._font_cache_key = font_key
        self._static_text_cache.clear()
        self._dynamic_text_cache.clear()

    def _build_chrome_surface(self) -> pygame.Surface:
        chrome = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        self._draw_background(chrome)
        self._draw_glass_panel(chrome, self.layout.title_badge, accent=self.theme.accent_secondary, strong=True)
        self._draw_board_chrome(chrome)
        self._draw_glass_panel(chrome, self.layout.preview_card, accent=self.theme.accent, strong=True)
        self._draw_glass_panel(chrome, self.layout.stats_card, accent=self.theme.accent_secondary)
        self._draw_glass_panel(chrome, self.layout.controls_card, accent=self.theme.accent_warm)
        return chrome

    def _build_overlay_surfaces(self) -> dict[str, pygame.Surface]:
        overlays: dict[str, pygame.Surface] = {}
        overlays["paused"] = self._build_overlay_surface(self.theme.accent)
        overlays["game_over"] = self._build_overlay_surface(self.theme.danger)
        return overlays

    def _build_overlay_surface(self, accent: tuple[int, int, int]) -> pygame.Surface:
        overlay = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        overlay.fill(self.theme.overlay_dim)
        self._draw_glass_panel(overlay, self.layout.overlay_card, accent=accent, strong=True, fill=self.theme.overlay_fill)
        return overlay

    def _draw_background(self, surface: pygame.Surface) -> None:
        height = self.layout.screen.height
        width = self.layout.screen.width
        for y in range(height):
            blend = y / max(1, height - 1)
            color = tuple(
                int(self.theme.background_top[index] + (self.theme.background_bottom[index] - self.theme.background_top[index]) * blend)
                for index in range(3)
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        for x in range(0, width, 44):
            pygame.draw.line(surface, self.theme.ambient_grid, (x, 0), (x, height))
        for y in range(0, height, 44):
            pygame.draw.line(surface, self.theme.ambient_grid, (0, y), (width, y))

        glow_surface = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, self.theme.ambient_glow_primary, (140, 92), 150)
        pygame.draw.circle(glow_surface, self.theme.ambient_glow_secondary, (710, 120), 120)
        pygame.draw.circle(glow_surface, self.theme.ambient_glow_primary, (660, 520), 170)
        pygame.draw.line(glow_surface, self.theme.ambient_grid, (0, 540), (800, 360), 2)
        pygame.draw.line(glow_surface, self.theme.ambient_grid, (0, 210), (800, 20), 2)
        surface.blit(glow_surface, (0, 0))

    def _draw_board_chrome(self, surface: pygame.Surface) -> None:
        glow = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        pygame.draw.rect(glow, self.theme.ambient_glow_primary, self.layout.board.inflate(18, 18), border_radius=28)
        surface.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.rect(surface, self.theme.board_fill, self.layout.board, border_radius=self.theme.panel_radius)
        pygame.draw.rect(surface, self.theme.board_tint, self.layout.board, 0, border_radius=self.theme.panel_radius)
        pygame.draw.rect(surface, self.theme.glass_edge, self.layout.board, 2, border_radius=self.theme.panel_radius)
        pygame.draw.line(
            surface,
            self.theme.glass_edge_soft,
            (self.layout.board.x + 12, self.layout.board.y + 12),
            (self.layout.board.right - 12, self.layout.board.y + 12),
            2,
        )

        for grid_x in range(GRID_WIDTH + 1):
            start = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.y)
            end = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.y + self.layout.board.height)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

        for grid_y in range(GRID_HEIGHT + 1):
            start = (self.layout.board.x, self.layout.board.y + grid_y * self.grid_size)
            end = (self.layout.board.x + self.layout.board.width, self.layout.board.y + grid_y * self.grid_size)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

    def _draw_glass_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        *,
        accent: tuple[int, int, int],
        strong: bool = False,
        fill: tuple[int, int, int, int] | None = None,
    ) -> None:
        shadow_rect = rect.move(0, 10)
        pygame.draw.rect(surface, self.theme.panel_shadow, shadow_rect, border_radius=self.theme.panel_radius)
        panel_fill = self.theme.glass_fill_strong if strong else self.theme.glass_fill
        pygame.draw.rect(surface, fill or panel_fill, rect, border_radius=self.theme.panel_radius)
        pygame.draw.rect(surface, (*accent, 164), rect, 2, border_radius=self.theme.panel_radius)
        highlight = pygame.Rect(rect.x + 12, rect.y + 10, rect.width - 24, max(10, rect.height // 4))
        pygame.draw.rect(surface, self.theme.glass_edge_soft, highlight, border_radius=18)

    def _draw_title(self, surface: pygame.Surface, fonts: FontBundle) -> None:
        title = self._get_static_text("title", "TETRIS", fonts.title, self.theme.text)
        subtitle = self._get_static_text("subtitle", "neon glass release build", fonts.small, self.theme.text_muted)
        surface.blit(title, title.get_rect(center=(self.layout.title_badge.centerx, self.layout.title_badge.centery - 6)))
        surface.blit(subtitle, subtitle.get_rect(center=(self.layout.title_badge.centerx, self.layout.title_badge.centery + 16)))

    def draw_board(self, surface: pygame.Surface, state: GameState) -> None:
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
        self._blit_card_heading(surface, "next_heading", "NEXT PIECE", fonts.small, self.theme.text, self.layout.preview_card)
        self._blit_card_heading(surface, "stats_heading", "RUN DATA", fonts.small, self.theme.text, self.layout.stats_card)
        self._blit_card_heading(surface, "controls_heading", "COMMAND GRID", fonts.small, self.theme.text, self.layout.controls_card)

        self.draw_preview(surface, state.next_piece)
        self.draw_stats(surface, state, fonts)
        self.draw_controls(surface, fonts)

    def draw_preview(self, surface: pygame.Surface, piece: Tetromino) -> None:
        piece_width = len(piece.shape[0]) * self.grid_size
        piece_height = len(piece.shape) * self.grid_size
        origin = (
            self.layout.preview_card.centerx - piece_width // 2,
            self.layout.preview_card.centery - piece_height // 2 + 10,
        )
        self.draw_piece(surface, piece, origin, board_positioned=False)

    def draw_stats(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        stats = [
            ("SCORE", str(state.score)),
            ("LEVEL", str(state.level)),
            ("LINES", str(state.lines_cleared)),
        ]
        for index, (label, value) in enumerate(stats):
            top = self.layout.stats_card.y + 44 + index * 30
            label_surface = self._get_static_text(f"stat-label-{label}", label, fonts.small, self.theme.text_muted)
            value_surface = self._get_dynamic_text(f"stat-value-{label}", value, fonts.body, self.theme.text)
            surface.blit(label_surface, (self.layout.stats_card.x + 18, top))
            surface.blit(value_surface, (self.layout.stats_card.right - value_surface.get_width() - 18, top - 6))

    def draw_controls(self, surface: pygame.Surface, fonts: FontBundle) -> None:
        controls = [
            "A / D   Shift",
            "W       Rotate",
            "S       Soft Drop",
            "Space   Hard Drop",
            "P       Pause",
            "R       Restart",
            "",
            "Bomb blocks clear the",
            "8 surrounding cells.",
        ]
        for index, text in enumerate(controls):
            key = f"control-{index}"
            color = self.theme.text if text else self.theme.text_muted
            label = self._get_static_text(key, text, fonts.small, color)
            surface.blit(label, (self.layout.controls_card.x + 18, self.layout.controls_card.y + 44 + index * 20))

    def draw_overlay(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        if state.game_over:
            surface.blit(self._overlay_surfaces["game_over"], (0, 0))
            title = self._get_static_text("overlay-game-over", "GAME OVER", fonts.title, self.theme.danger)
            score = self._get_dynamic_text("overlay-score", f"FINAL SCORE  {state.score}", fonts.body, self.theme.text)
            restart = self._get_static_text("overlay-restart", "Press R to drop back in", fonts.small, self.theme.text_muted)
            surface.blit(title, title.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 78)))
            surface.blit(score, score.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 150)))
            surface.blit(restart, restart.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 204)))
            return

        if state.paused:
            surface.blit(self._overlay_surfaces["paused"], (0, 0))
            title = self._get_static_text("overlay-paused", "PAUSED", fonts.title, self.theme.accent)
            body = self._get_static_text("overlay-body", "Press P to resume the run", fonts.small, self.theme.text_muted)
            surface.blit(title, title.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 88)))
            surface.blit(body, body.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 166)))

    def draw_block(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*color, 80), pygame.Rect(10, 10, rect.width, rect.height), border_radius=self.theme.block_radius + 6)
        surface.blit(glow, (rect.x - 10, rect.y - 10), special_flags=pygame.BLEND_RGBA_ADD)

        pygame.draw.rect(surface, color, rect, border_radius=self.theme.block_radius)
        pygame.draw.rect(surface, self.theme.glass_edge_soft, rect, 1, border_radius=self.theme.block_radius)
        shine = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 6, max(8, rect.height // 2))
        pygame.draw.rect(
            surface,
            tuple(min(255, channel + self.theme.highlight_boost) for channel in color),
            shine,
            border_radius=max(4, self.theme.block_radius - 2),
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
                pygame.draw.circle(surface, self.theme.text, (rect.centerx, rect.y - 8), 3)

    def draw_explosion(self, surface: pygame.Surface, state: GameState) -> None:
        if not state.explosion_active:
            return

        progress = min(1.0, state.explosion_time / 0.5)
        for grid_x, grid_y in state.explosion_positions:
            center_x = self.layout.board.x + grid_x * self.grid_size + self.grid_size // 2
            center_y = self.layout.board.y + grid_y * self.grid_size + self.grid_size // 2
            radius = int(self.grid_size * 0.75 * progress)
            explosion_color = (255, max(0, int(255 * (1 - progress))), 42)
            pygame.draw.circle(surface, explosion_color, (center_x, center_y), radius)
            for angle in range(0, 360, 45):
                end_x = center_x + int(radius * 1.5 * math.cos(math.radians(angle)))
                end_y = center_y + int(radius * 1.5 * math.sin(math.radians(angle)))
                pygame.draw.line(surface, self.theme.fuse, (center_x, center_y), (end_x, end_y), 2)

    def _blit_card_heading(
        self,
        surface: pygame.Surface,
        cache_key: str,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
        rect: pygame.Rect,
    ) -> None:
        label = self._get_static_text(cache_key, text, font, color)
        surface.blit(label, (rect.x + 18, rect.y + 14))
        pygame.draw.line(surface, self.theme.glass_edge_soft, (rect.x + 18, rect.y + 36), (rect.right - 18, rect.y + 36), 1)

    def _get_static_text(
        self,
        cache_key: str,
        text: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
    ) -> pygame.Surface:
        cached = self._static_text_cache.get(cache_key)
        if cached is None:
            cached = font.render(text, True, color)
            self._static_text_cache[cache_key] = cached
        return cached

    def _get_dynamic_text(
        self,
        cache_key: str,
        value: str,
        font: pygame.font.Font,
        color: tuple[int, int, int],
    ) -> pygame.Surface:
        dynamic_key = (cache_key, value)
        cached = self._dynamic_text_cache.get(dynamic_key)
        if cached is None:
            cached = font.render(value, True, color)
            self._dynamic_text_cache[dynamic_key] = cached
        return cached
