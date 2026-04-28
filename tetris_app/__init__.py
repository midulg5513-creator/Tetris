from __future__ import annotations


def main(max_frames: int | None = None) -> int:
    from .app import main as app_main

    return app_main(max_frames=max_frames)

__all__ = ["main"]
