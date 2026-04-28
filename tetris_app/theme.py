from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]
AlphaColor = tuple[int, int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    background_top: Color = (148, 100, 58)
    background_bottom: Color = (136, 90, 50)
    backdrop_border: Color = (168, 122, 76)
    backdrop_pattern: AlphaColor = (255, 244, 219, 22)
    backdrop_accent_left: AlphaColor = (110, 70, 40, 34)
    backdrop_accent_right: AlphaColor = (196, 156, 104, 20)
    backdrop_accent_bottom: AlphaColor = (109, 70, 40, 24)
    cabinet_glow: AlphaColor = (255, 238, 198, 22)
    cabinet_shadow: AlphaColor = (56, 33, 18, 86)
    cabinet_fill_top: Color = (176, 126, 77)
    cabinet_fill_bottom: Color = (155, 105, 61)
    cabinet_border: Color = (109, 69, 39)
    cabinet_rim: Color = (194, 150, 98)
    sidebar_fill_top: Color = (175, 127, 79)
    sidebar_fill_bottom: Color = (162, 115, 71)
    sidebar_border: Color = (112, 72, 41)
    board_shadow: AlphaColor = (66, 40, 20, 86)
    board_frame_outer: Color = (129, 82, 43)
    board_frame_inner: Color = (164, 112, 63)
    machine_head_fill: Color = (177, 126, 74)
    machine_head_border: Color = (112, 72, 40)
    score_track_fill: Color = (94, 60, 36)
    score_track_border: Color = (73, 45, 25)
    score_light_on: Color = (255, 228, 145)
    score_light_glow: AlphaColor = (255, 223, 128, 74)
    score_light_off: Color = (118, 86, 54)
    board_fill_top: Color = (90, 57, 34)
    board_fill_bottom: Color = (82, 50, 29)
    board_border: Color = (114, 73, 41)
    grid_line: AlphaColor = (54, 32, 18, 88)
    card_fill: Color = (204, 157, 100)
    card_fill_soft: Color = (193, 146, 92)
    card_border: Color = (124, 84, 48)
    card_shadow: AlphaColor = (68, 42, 22, 48)
    card_divider: Color = (116, 80, 49)
    text: Color = (66, 44, 25)
    text_muted: Color = (93, 66, 41)
    title: Color = (246, 222, 159)
    accent: Color = (248, 210, 113)
    accent_secondary: Color = (226, 188, 122)
    danger: Color = (139, 62, 45)
    overlay_dim: AlphaColor = (50, 28, 14, 118)
    overlay_card_fill: Color = (203, 156, 98)
    overlay_card_border: Color = (117, 78, 44)
    block_border_darkness: int = -38
    block_shadow_darkness: int = -18
    block_highlight_lightness: int = 24
    block_face_lightness: int = 10
    block_radius: int = 2
    panel_radius: int = 8
    board_frame_radius: int = 6


def build_theme() -> Theme:
    return Theme()
