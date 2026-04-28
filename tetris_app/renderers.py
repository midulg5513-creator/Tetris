from __future__ import annotations

import math

import pygame

from .game_state import GRID_HEIGHT, GRID_WIDTH, GameState
from .layout import GameLayout
from .pieces import Tetromino
from .resources import FontBundle
from .theme import Theme


def adjust_color(color: tuple[int, int, int], delta: int) -> tuple[int, int, int]:
    return tuple(max(0, min(255, channel + delta)) for channel in color)


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

    def _get_title_badge_rect(self) -> pygame.Rect:
        return pygame.Rect(
            self.layout.machine_head.x + 12,
            self.layout.machine_head.y + 8,
            84,
            self.layout.machine_head.height - 16,
        )

    def _get_score_bezel_rect(self) -> pygame.Rect:
        return self.layout.score_track.inflate(14, 10)

    def _build_chrome_surface(self) -> pygame.Surface:
        chrome = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        self._draw_background(chrome)
        self._draw_cabinet(chrome)
        self._draw_machine_head_chrome(chrome)
        self._draw_board_chrome(chrome)
        self._draw_sidebar_panel(chrome)
        self._draw_panel_section(chrome, self.layout.preview_card, self.theme.card_fill, grain_dark_alpha=2, grain_light_alpha=1, sheen_alpha=18)
        self._draw_panel_section(chrome, self.layout.stats_card, self.theme.card_fill, grain_dark_alpha=0, grain_light_alpha=0, sheen_alpha=16)
        self._draw_panel_section(chrome, self.layout.controls_card, self.theme.card_fill_soft, grain_dark_alpha=0, grain_light_alpha=0, sheen_alpha=14)
        return chrome

    def _build_overlay_surfaces(self) -> dict[str, pygame.Surface]:
        return {
            "paused": self._build_overlay_surface(),
            "game_over": self._build_overlay_surface(),
        }

    def _build_overlay_surface(self) -> pygame.Surface:
        overlay = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        overlay.fill(self.theme.overlay_dim)
        shadow = self.layout.overlay_card.move(0, 10)
        pygame.draw.rect(overlay, self.theme.card_shadow, shadow, border_radius=self.theme.panel_radius)
        pygame.draw.rect(overlay, self.theme.overlay_card_fill, self.layout.overlay_card, border_radius=self.theme.panel_radius)
        pygame.draw.rect(
            overlay,
            self.theme.overlay_card_border,
            self.layout.overlay_card,
            2,
            border_radius=self.theme.panel_radius,
        )
        return overlay

    def _draw_background(self, surface: pygame.Surface) -> None:
        width = self.layout.screen.width
        height = self.layout.screen.height
        for y in range(height):
            blend = y / max(1, height - 1)
            color = tuple(
                int(self.theme.background_top[index] + (self.theme.background_bottom[index] - self.theme.background_top[index]) * blend)
                for index in range(3)
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        accent_surface = pygame.Surface(self.layout.screen.size, pygame.SRCALPHA)
        pygame.draw.rect(accent_surface, self.theme.backdrop_accent_left, pygame.Rect(0, 0, width // 5, height))
        pygame.draw.rect(accent_surface, self.theme.backdrop_accent_right, pygame.Rect(width - 140, 0, 140, height))
        pygame.draw.rect(accent_surface, self.theme.backdrop_accent_bottom, pygame.Rect(0, height - 120, width, 120))
        top_glow = pygame.Rect(self.layout.cabinet.x - 90, self.layout.cabinet.y - 40, self.layout.cabinet.width + 180, 180)
        floor_shadow = pygame.Rect(self.layout.cabinet.x - 40, self.layout.cabinet.bottom - 24, self.layout.cabinet.width + 80, 82)
        cabinet_glow = self.layout.cabinet.inflate(56, 22)
        pygame.draw.ellipse(accent_surface, (255, 243, 214, 20), top_glow)
        pygame.draw.ellipse(accent_surface, (79, 49, 27, 24), floor_shadow)
        pygame.draw.rect(accent_surface, self.theme.cabinet_glow, cabinet_glow, border_radius=24)
        surface.blit(accent_surface, (0, 0))

        pygame.draw.rect(surface, self.theme.backdrop_border, self.layout.screen.inflate(-18, -18), 1, border_radius=8)

    def _blend_color(
        self,
        start: tuple[int, int, int],
        end: tuple[int, int, int],
        ratio: float,
    ) -> tuple[int, int, int]:
        return tuple(int(start[index] + (end[index] - start[index]) * ratio) for index in range(3))

    def _mask_rounded_surface(self, surface: pygame.Surface, radius: int) -> None:
        mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), mask.get_rect(), border_radius=radius)
        surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _draw_wood_grain(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        base: tuple[int, int, int],
        *,
        orientation: str,
        seed: int,
        density: int = 10,
        dark_alpha: int = 30,
        light_alpha: int = 14,
        knots: bool = False,
    ) -> None:
        if dark_alpha <= 0 and light_alpha <= 0 and not knots:
            return

        dark = (*adjust_color(base, -20), dark_alpha)
        light = (*adjust_color(base, 12), light_alpha)
        step = 9

        if orientation == "horizontal":
            for offset in range(-6, rect.height + 8, density):
                dark_points: list[tuple[int, int]] = []
                light_points: list[tuple[int, int]] = []
                for x in range(-8, rect.width + 8, step):
                    wave = int(
                        math.sin((x + seed * 5) * 0.03 + offset * 0.16) * 1.6
                        + math.sin((x + seed * 11) * 0.08) * 0.8
                    )
                    dark_points.append((x, offset + wave))
                    light_points.append((x, offset + wave + 2))
                pygame.draw.lines(surface, dark, False, dark_points, 1)
                pygame.draw.lines(surface, light, False, light_points, 1)
        else:
            for offset in range(-6, rect.width + 8, density):
                dark_points = []
                light_points = []
                for y in range(-8, rect.height + 8, step):
                    wave = int(
                        math.sin((y + seed * 7) * 0.028 + offset * 0.18) * 1.8
                        + math.sin((y + seed * 13) * 0.08) * 0.7
                    )
                    dark_points.append((offset + wave, y))
                    light_points.append((offset + wave + 2, y))
                pygame.draw.lines(surface, dark, False, dark_points, 1)
                pygame.draw.lines(surface, light, False, light_points, 1)

        if not knots or rect.width < 170 or rect.height < 140:
            return

        knot_count = max(1, (rect.width * rect.height) // 85000)
        for index in range(knot_count):
            knot_width = 20 + ((seed + index * 19) % 16)
            knot_height = 10 + ((seed + index * 11) % 8)
            if orientation == "vertical":
                knot_width, knot_height = knot_height + 4, knot_width + 8

            span_x = max(1, rect.width - knot_width - 20)
            span_y = max(1, rect.height - knot_height - 20)
            knot_x = 10 + ((seed * 37 + index * 61) % span_x)
            knot_y = 10 + ((seed * 53 + index * 47) % span_y)
            knot_rect = pygame.Rect(knot_x, knot_y, knot_width, knot_height)

            outer = (*adjust_color(base, -24), 42)
            inner = (*adjust_color(base, 14), 20)
            pygame.draw.ellipse(surface, outer, knot_rect, 1)
            inner_rect = knot_rect.inflate(-6, -4)
            if inner_rect.width > 4 and inner_rect.height > 4:
                pygame.draw.ellipse(surface, inner, inner_rect, 1)

    def _draw_wood_panel(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        top_color: tuple[int, int, int],
        bottom_color: tuple[int, int, int],
        border_color: tuple[int, int, int],
        *,
        border_radius: int,
        orientation: str,
        seed: int,
        inset: bool = False,
        grain_density: int = 12,
        grain_dark_alpha: int = 30,
        grain_light_alpha: int = 14,
        knots: bool = False,
    ) -> None:
        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        local_rect = panel.get_rect()

        if orientation == "horizontal":
            for y in range(local_rect.height):
                blend = y / max(1, local_rect.height - 1)
                color = self._blend_color(top_color, bottom_color, blend)
                pygame.draw.line(panel, color, (0, y), (local_rect.width, y))
        else:
            for x in range(local_rect.width):
                blend = x / max(1, local_rect.width - 1)
                color = self._blend_color(top_color, bottom_color, blend)
                pygame.draw.line(panel, color, (x, 0), (x, local_rect.height))

        self._draw_wood_grain(
            panel,
            local_rect,
            self._blend_color(top_color, bottom_color, 0.45),
            orientation=orientation,
            seed=seed,
            density=grain_density,
            dark_alpha=grain_dark_alpha,
            light_alpha=grain_light_alpha,
            knots=knots,
        )

        if inset:
            inner_shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(inner_shadow, (42, 25, 14, 52), local_rect, 4, border_radius=border_radius)
            panel.blit(inner_shadow, (0, 0))

        self._mask_rounded_surface(panel, border_radius)
        surface.blit(panel, rect.topleft)
        pygame.draw.rect(surface, border_color, rect, 2, border_radius=border_radius)

        highlight_rect = rect.inflate(-10, -10)
        if highlight_rect.width > 0 and highlight_rect.height > 0:
            pygame.draw.rect(surface, adjust_color(top_color, 18), highlight_rect, 1, border_radius=max(2, border_radius - 3))

    def _draw_cabinet(self, surface: pygame.Surface) -> None:
        shadow = self.layout.cabinet.move(0, 10)
        pygame.draw.rect(surface, self.theme.cabinet_shadow, shadow, border_radius=14)
        self._draw_wood_panel(
            surface,
            self.layout.cabinet,
            self.theme.cabinet_fill_top,
            self.theme.cabinet_fill_bottom,
            self.theme.cabinet_border,
            border_radius=14,
            orientation="vertical",
            seed=7,
            grain_density=26,
            grain_dark_alpha=18,
            grain_light_alpha=6,
        )
        inner_rim = self.layout.cabinet.inflate(-12, -12)
        pygame.draw.rect(surface, self.theme.cabinet_rim, inner_rim, 1, border_radius=10)

        left_post = pygame.Rect(self.layout.cabinet.x + 14, self.layout.cabinet.y + 28, 18, self.layout.cabinet.height - 56)
        right_post = pygame.Rect(
            self.layout.cabinet.right - 32,
            self.layout.cabinet.y + 28,
            18,
            self.layout.cabinet.height - 56,
        )
        post_top = adjust_color(self.theme.cabinet_fill_top, -18)
        post_bottom = adjust_color(self.theme.cabinet_fill_bottom, -26)
        self._draw_wood_panel(
            surface,
            left_post,
            post_top,
            post_bottom,
            adjust_color(self.theme.cabinet_border, -8),
            border_radius=6,
            orientation="vertical",
            seed=13,
            grain_density=22,
            grain_dark_alpha=16,
            grain_light_alpha=6,
        )
        self._draw_wood_panel(
            surface,
            right_post,
            post_top,
            post_bottom,
            adjust_color(self.theme.cabinet_border, -8),
            border_radius=6,
            orientation="vertical",
            seed=17,
            grain_density=22,
            grain_dark_alpha=16,
            grain_light_alpha=6,
        )

    def _draw_board_chrome(self, surface: pygame.Surface) -> None:
        shadow_rect = self.layout.board_frame.move(0, 8)
        pygame.draw.rect(surface, self.theme.board_shadow, shadow_rect, border_radius=self.theme.board_frame_radius + 2)
        inner_frame = self.layout.board_frame.inflate(-10, -10)
        self._draw_wood_panel(
            surface,
            self.layout.board_frame,
            self.theme.board_frame_outer,
            adjust_color(self.theme.board_frame_outer, -16),
            adjust_color(self.theme.board_frame_outer, -28),
            border_radius=self.theme.board_frame_radius,
            orientation="vertical",
            seed=23,
            grain_density=22,
            grain_dark_alpha=18,
            grain_light_alpha=6,
        )
        self._draw_wood_panel(
            surface,
            inner_frame,
            self.theme.board_frame_inner,
            adjust_color(self.theme.board_frame_inner, -12),
            adjust_color(self.theme.board_frame_outer, -12),
            border_radius=self.theme.board_frame_radius - 2,
            orientation="vertical",
            seed=29,
            inset=True,
            grain_density=24,
            grain_dark_alpha=12,
            grain_light_alpha=4,
        )
        self._draw_wood_panel(
            surface,
            self.layout.board,
            self.theme.board_fill_top,
            self.theme.board_fill_bottom,
            self.theme.board_border,
            border_radius=6,
            orientation="horizontal",
            seed=31,
            inset=True,
            grain_density=40,
            grain_dark_alpha=0,
            grain_light_alpha=0,
        )
        pygame.draw.rect(surface, (39, 24, 15), pygame.Rect(self.layout.board_frame.x, self.layout.board_frame.bottom - 10, self.layout.board_frame.width, 10))

        for grid_x in range(GRID_WIDTH + 1):
            start = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.y)
            end = (self.layout.board.x + grid_x * self.grid_size, self.layout.board.bottom)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

        for grid_y in range(GRID_HEIGHT + 1):
            start = (self.layout.board.x, self.layout.board.y + grid_y * self.grid_size)
            end = (self.layout.board.right, self.layout.board.y + grid_y * self.grid_size)
            pygame.draw.line(surface, self.theme.grid_line, start, end)

    def _draw_machine_head_chrome(self, surface: pygame.Surface) -> None:
        shadow = self.layout.machine_head.move(0, 6)
        pygame.draw.rect(surface, self.theme.board_shadow, shadow, border_radius=8)
        self._draw_wood_panel(
            surface,
            self.layout.machine_head,
            self.theme.machine_head_fill,
            adjust_color(self.theme.machine_head_fill, -10),
            self.theme.machine_head_border,
            border_radius=8,
            orientation="horizontal",
            seed=37,
            grain_density=26,
            grain_dark_alpha=10,
            grain_light_alpha=4,
        )
        top_sheen = pygame.Surface(self.layout.machine_head.size, pygame.SRCALPHA)
        pygame.draw.line(
            top_sheen,
            (255, 244, 214, 26),
            (10, 7),
            (self.layout.machine_head.width - 10, 7),
            1,
        )
        self._mask_rounded_surface(top_sheen, 8)
        surface.blit(top_sheen, self.layout.machine_head.topleft)

        badge_rect = self._get_title_badge_rect()
        badge_shadow = badge_rect.move(0, 2)
        pygame.draw.rect(surface, (57, 35, 20, 52), badge_shadow, border_radius=6)
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_fill, -44), badge_rect, border_radius=6)
        badge_inner = badge_rect.inflate(-4, -4)
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_fill, -28), badge_inner, border_radius=4)
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_border, -10), badge_rect, 1, border_radius=6)
        pygame.draw.line(
            surface,
            (255, 240, 205, 42),
            (badge_inner.x + 5, badge_inner.y + 3),
            (badge_inner.right - 5, badge_inner.y + 3),
            1,
        )
        for center_x in (badge_rect.x + 8, badge_rect.right - 8):
            pygame.draw.circle(surface, adjust_color(self.theme.machine_head_border, -20), (center_x, badge_rect.centery), 2)
            pygame.draw.circle(surface, adjust_color(self.theme.machine_head_fill, 14), (center_x - 1, badge_rect.centery - 1), 1)

        score_bezel = self._get_score_bezel_rect()
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_fill, -38), score_bezel, border_radius=7)
        bezel_inner = score_bezel.inflate(-4, -4)
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_fill, -20), bezel_inner, border_radius=5)
        pygame.draw.rect(surface, adjust_color(self.theme.machine_head_border, -12), score_bezel, 1, border_radius=7)
        pygame.draw.rect(surface, self.theme.score_track_fill, self.layout.score_track, border_radius=4)
        pygame.draw.rect(surface, self.theme.score_track_border, self.layout.score_track, 1, border_radius=4)
        pygame.draw.line(
            surface,
            (255, 245, 226, 34),
            (self.layout.score_track.x + 5, self.layout.score_track.y + 3),
            (self.layout.score_track.right - 5, self.layout.score_track.y + 3),
            1,
        )
        for center_x in (score_bezel.x + 8, score_bezel.right - 8):
            pygame.draw.circle(surface, adjust_color(self.theme.machine_head_border, -18), (center_x, score_bezel.centery), 2)

    def _draw_sidebar_panel(self, surface: pygame.Surface) -> None:
        shadow = self.layout.sidebar.move(0, 6)
        pygame.draw.rect(surface, self.theme.card_shadow, shadow, border_radius=self.theme.panel_radius + 2)
        self._draw_wood_panel(
            surface,
            self.layout.sidebar,
            self.theme.sidebar_fill_top,
            self.theme.sidebar_fill_bottom,
            self.theme.sidebar_border,
            border_radius=self.theme.panel_radius + 2,
            orientation="vertical",
            seed=41,
            inset=True,
            grain_density=28,
            grain_dark_alpha=4,
            grain_light_alpha=1,
        )

    def _draw_panel_section(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        fill: tuple[int, int, int],
        *,
        grain_dark_alpha: int,
        grain_light_alpha: int,
        sheen_alpha: int,
    ) -> None:
        recess = rect.inflate(8, 8)
        pygame.draw.rect(surface, self.theme.card_shadow, recess, border_radius=self.theme.panel_radius + 1)
        self._draw_wood_panel(
            surface,
            rect,
            fill,
            adjust_color(fill, -8),
            self.theme.card_border,
            border_radius=self.theme.panel_radius,
            orientation="horizontal",
            seed=rect.x + rect.y,
            inset=True,
            grain_density=24,
            grain_dark_alpha=grain_dark_alpha,
            grain_light_alpha=grain_light_alpha,
        )
        sheen = pygame.Surface(rect.size, pygame.SRCALPHA)
        for y in range(rect.height // 2):
            alpha = max(0, sheen_alpha - int((y / max(1, rect.height // 2)) * sheen_alpha))
            pygame.draw.line(sheen, (255, 246, 224, alpha), (10, y + 8), (rect.width - 10, y + 8))
        self._mask_rounded_surface(sheen, self.theme.panel_radius)
        surface.blit(sheen, rect.topleft)

    def _draw_title(self, surface: pygame.Surface, fonts: FontBundle) -> None:
        header_font = fonts.tiny or fonts.small
        badge_rect = self._get_title_badge_rect()
        title_shadow = self._get_static_text("title-shadow", "TETRIS", header_font, adjust_color(self.theme.machine_head_border, -30))
        title = self._get_static_text("title", "TETRIS", header_font, self.theme.title)
        title_pos = title.get_rect(center=(badge_rect.centerx, badge_rect.centery + 1))
        shadow_pos = title_shadow.get_rect(center=(badge_rect.centerx, badge_rect.centery + 2))
        surface.blit(title_shadow, shadow_pos)
        surface.blit(title, title_pos)
        pygame.draw.line(
            surface,
            (255, 231, 176, 66),
            (badge_rect.x + 16, badge_rect.bottom - 5),
            (badge_rect.right - 16, badge_rect.bottom - 5),
            1,
        )

    def _draw_score_track(self, surface: pygame.Surface, state: GameState) -> None:
        lights = 8
        light_width = 14
        light_height = 8
        gap = 4
        total_width = lights * light_width + (lights - 1) * gap
        start_x = self.layout.score_track.centerx - total_width // 2
        start_y = self.layout.score_track.centery - light_height // 2
        lit_count = max(1, min(lights, state.level + 1))

        for index in range(lights):
            bezel = pygame.Rect(start_x + index * (light_width + gap), start_y, light_width, light_height)
            inner_rect = bezel.inflate(-2, -2)
            pygame.draw.rect(surface, adjust_color(self.theme.score_track_fill, 10), bezel, border_radius=3)
            pygame.draw.rect(surface, adjust_color(self.theme.score_track_fill, -16), bezel, 1, border_radius=3)
            if index < lit_count:
                glow = pygame.Surface((light_width + 12, light_height + 12), pygame.SRCALPHA)
                pygame.draw.rect(
                    glow,
                    self.theme.score_light_glow,
                    pygame.Rect(6, 6, light_width, light_height),
                    border_radius=4,
                )
                surface.blit(glow, (bezel.x - 6, bezel.y - 6))
                color = self.theme.score_light_on
                core = adjust_color(self.theme.score_light_on, 20)
            else:
                color = self.theme.score_light_off
                core = adjust_color(self.theme.score_light_off, -8)

            pygame.draw.rect(surface, color, inner_rect, border_radius=3)
            core_rect = inner_rect.inflate(-4, -3)
            if core_rect.width > 0 and core_rect.height > 0:
                pygame.draw.rect(surface, core, core_rect, border_radius=2)
            pygame.draw.line(
                surface,
                adjust_color(color, 18),
                (inner_rect.x + 2, inner_rect.y + 1),
                (inner_rect.right - 2, inner_rect.y + 1),
                1,
            )

    def draw_board(self, surface: pygame.Surface, state: GameState) -> None:
        self._draw_score_track(surface, state)
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

    def draw_sidebar(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        detail_font = fonts.tiny or fonts.small
        self._blit_card_heading(surface, "next_heading", "NEXT", detail_font, self.layout.preview_card)
        self._blit_card_heading(surface, "stats_heading", "STATUS", detail_font, self.layout.stats_card)
        self._blit_card_heading(surface, "controls_heading", "KEYS", detail_font, self.layout.controls_card)
        self.draw_preview(surface, state.next_piece)
        self.draw_stats(surface, state, fonts)
        self.draw_controls(surface, fonts)

    def draw_preview(self, surface: pygame.Surface, piece: Tetromino) -> None:
        piece_width = len(piece.shape[0]) * self.grid_size
        piece_height = len(piece.shape) * self.grid_size
        origin = (
            self.layout.preview_card.centerx - piece_width // 2,
            self.layout.preview_card.centery - piece_height // 2 + 8,
        )
        self.draw_piece(surface, piece, origin, board_positioned=False)

    def draw_stats(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        detail_font = fonts.tiny or fonts.small
        stats = [("Score", str(state.score)), ("Level", str(state.level)), ("Lines", str(state.lines_cleared))]
        for index, (label, value) in enumerate(stats):
            top = self.layout.stats_card.y + 44 + index * 32
            label_surface = self._get_static_text(f"stat-label-{label}", label, detail_font, self.theme.text_muted)
            value_surface = self._get_dynamic_text(f"stat-value-{label}", value, fonts.body, self.theme.text)
            surface.blit(label_surface, (self.layout.stats_card.x + 18, top))
            surface.blit(value_surface, (self.layout.stats_card.right - value_surface.get_width() - 18, top - 6))

    def draw_controls(self, surface: pygame.Surface, fonts: FontBundle) -> None:
        detail_font = fonts.tiny or fonts.small
        controls = [
            "Move      A / D",
            "Rotate    W",
            "Soft drop S",
            "Hard drop Space",
            "Pause     P",
            "Restart   R",
        ]
        for index, text in enumerate(controls):
            key = f"control-{index}"
            color = self.theme.text if text else self.theme.text_muted
            label = self._get_static_text(key, text, detail_font, color)
            surface.blit(label, (self.layout.controls_card.x + 18, self.layout.controls_card.y + 44 + index * 18))

    def draw_overlay(self, surface: pygame.Surface, state: GameState, fonts: FontBundle) -> None:
        if state.game_over:
            surface.blit(self._overlay_surfaces["game_over"], (0, 0))
            title = self._get_static_text("overlay-game-over", "Game Over", fonts.body, self.theme.danger)
            score = self._get_dynamic_text("overlay-score", f"Score  {state.score}", fonts.body, self.theme.text)
            restart = self._get_static_text("overlay-restart", "Press R to restart", fonts.tiny or fonts.small, self.theme.text_muted)
            surface.blit(title, title.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 56)))
            surface.blit(score, score.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 106)))
            surface.blit(restart, restart.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 148)))
            return

        if state.paused:
            surface.blit(self._overlay_surfaces["paused"], (0, 0))
            title = self._get_static_text("overlay-paused", "Paused", fonts.body, self.theme.title)
            body = self._get_static_text("overlay-body", "Press P to continue", fonts.tiny or fonts.small, self.theme.text_muted)
            surface.blit(title, title.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 58)))
            surface.blit(body, body.get_rect(center=(self.layout.overlay_card.centerx, self.layout.overlay_card.y + 108)))

    def draw_block(self, surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]) -> None:
        outer = rect.inflate(-2, -2)
        border = adjust_color(color, self.theme.block_border_darkness)
        shadow = adjust_color(color, self.theme.block_shadow_darkness)
        face = adjust_color(color, self.theme.block_face_lightness)
        highlight = adjust_color(color, self.theme.block_highlight_lightness)

        pygame.draw.rect(surface, border, outer, border_radius=self.theme.block_radius)

        top_facet = [
            (outer.left + 1, outer.top + 1),
            (outer.right - 1, outer.top + 1),
            (outer.right - 5, outer.top + 5),
            (outer.left + 5, outer.top + 5),
        ]
        left_facet = [
            (outer.left + 1, outer.top + 1),
            (outer.left + 5, outer.top + 5),
            (outer.left + 5, outer.bottom - 5),
            (outer.left + 1, outer.bottom - 1),
        ]
        right_facet = [
            (outer.right - 1, outer.top + 1),
            (outer.right - 5, outer.top + 5),
            (outer.right - 5, outer.bottom - 5),
            (outer.right - 1, outer.bottom - 1),
        ]
        bottom_facet = [
            (outer.left + 1, outer.bottom - 1),
            (outer.left + 5, outer.bottom - 5),
            (outer.right - 5, outer.bottom - 5),
            (outer.right - 1, outer.bottom - 1),
        ]
        pygame.draw.polygon(surface, highlight, top_facet)
        pygame.draw.polygon(surface, face, left_facet)
        pygame.draw.polygon(surface, shadow, right_facet)
        pygame.draw.polygon(surface, shadow, bottom_facet)

        center = outer.inflate(-10, -10)
        if center.width < 8 or center.height < 8:
            center = outer.inflate(-6, -6)
        pygame.draw.rect(surface, face, center, border_radius=max(2, self.theme.block_radius - 1))
        pygame.draw.rect(surface, adjust_color(border, 18), center, 1, border_radius=max(2, self.theme.block_radius - 1))

        inner_highlight = pygame.Rect(center.x + 2, center.y + 2, center.width - 4, max(3, center.height // 3))
        if inner_highlight.width > 0 and inner_highlight.height > 0:
            pygame.draw.rect(surface, highlight, inner_highlight, border_radius=2)

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

    def _blit_card_heading(self, surface: pygame.Surface, cache_key: str, text: str, font: pygame.font.Font, rect: pygame.Rect) -> None:
        label = self._get_static_text(cache_key, text, font, self.theme.text)
        surface.blit(label, (rect.x + 16, rect.y + 12))
        pygame.draw.line(surface, self.theme.card_divider, (rect.x + 16, rect.y + 34), (rect.right - 16, rect.y + 34), 1)

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
