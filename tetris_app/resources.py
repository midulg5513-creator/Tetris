from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pygame


LOGGER = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT_DIR / "assets" / "fonts" / "NotoSansSC-Regular.ttf"
SYSTEM_FONT_NAMES = (
    "simhei",
    "microsoftyahei",
    "kaiti",
    "simsunnsimsun",
    "Arial",
)


@dataclass(frozen=True)
class FontBundle:
    body: pygame.font.Font
    small: pygame.font.Font
    title: pygame.font.Font


def initialize_runtime(size: tuple[int, int], caption: str) -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(caption)
    return screen


def shutdown_runtime() -> None:
    pygame.quit()


def load_font(size: int) -> pygame.font.Font:
    if FONT_PATH.exists():
        try:
            return pygame.font.Font(str(FONT_PATH), size)
        except (FileNotFoundError, OSError, pygame.error) as exc:
            LOGGER.warning("Failed to load bundled font '%s': %s", FONT_PATH, exc)
    else:
        LOGGER.warning("Bundled font is missing at '%s'; falling back to system fonts.", FONT_PATH)

    for name in SYSTEM_FONT_NAMES:
        try:
            font = pygame.font.SysFont(name, size)
            if font.render("测试", True, (255, 255, 255)).get_width() > 0:
                return font
        except pygame.error as exc:
            LOGGER.warning("System font '%s' could not be loaded: %s", name, exc)

    LOGGER.warning("Falling back to pygame default font for size %s.", size)
    return pygame.font.Font(None, size)


def create_font_bundle() -> FontBundle:
    return FontBundle(
        body=load_font(36),
        small=load_font(24),
        title=load_font(64),
    )
