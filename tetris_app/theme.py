from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]
AlphaColor = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    background_top: Color = (3, 12, 28)
    background_bottom: Color = (6, 18, 40)
    ambient_grid: AlphaColor = (120, 226, 255, 18)
    ambient_glow_primary: AlphaColor = (46, 240, 255, 70)
    ambient_glow_secondary: AlphaColor = (143, 255, 205, 48)
    board_fill: AlphaColor = (8, 18, 34, 220)
    board_tint: AlphaColor = (42, 112, 156, 36)
    glass_fill: AlphaColor = (255, 255, 255, 28)
    glass_fill_strong: AlphaColor = (255, 255, 255, 42)
    glass_edge: AlphaColor = (104, 245, 255, 176)
    glass_edge_soft: AlphaColor = (255, 255, 255, 92)
    panel_shadow: AlphaColor = (2, 8, 20, 130)
    grid_line: AlphaColor = (93, 150, 198, 42)
    text: Color = (241, 248, 255)
    text_muted: Color = (168, 192, 220)
    accent: Color = (90, 244, 255)
    accent_secondary: Color = (145, 255, 204)
    accent_warm: Color = (255, 228, 132)
    danger: Color = (255, 98, 150)
    fuse: Color = (255, 228, 92)
    overlay_dim: AlphaColor = (3, 8, 18, 176)
    overlay_fill: AlphaColor = (18, 30, 52, 210)
    highlight_boost: int = 58
    block_radius: int = 9
    panel_radius: int = 24


def build_theme() -> Theme:
    return Theme()
