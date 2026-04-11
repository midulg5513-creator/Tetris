from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    background_color: Color = (40, 40, 60)
    panel_background: Color = (12, 16, 28)
    panel_border: Color = (255, 255, 255)
    grid_line: Color = (46, 58, 82)
    text: Color = (235, 242, 255)
    accent: Color = (255, 230, 120)
    danger: Color = (255, 84, 112)
    fuse: Color = (255, 224, 90)
    highlight_boost: int = 50
    block_radius: int = 6
    panel_radius: int = 16


def build_theme() -> Theme:
    return Theme()
