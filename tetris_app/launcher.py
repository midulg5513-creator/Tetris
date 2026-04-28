from __future__ import annotations

import sys
import traceback


def _build_startup_help(exc: BaseException) -> str:
    return "\n".join(
        [
            "Failed to start the game runtime.",
            f"Python interpreter: {sys.executable}",
            f"Error: {exc}",
            "",
            "This usually means the wrong Python interpreter is running the game,",
            "or the current interpreter has a broken pygame/SDL installation.",
            "",
            "Try these commands in the same interpreter:",
            f'"{sys.executable}" -m pip uninstall -y pygame pygame-ce',
            f'"{sys.executable}" -m pip install --no-cache-dir --force-reinstall pygame==2.6.1',
            "",
            "Then launch again with one of:",
            f'"{sys.executable}" "main.py"',
            f'"{sys.executable}" -m tetris_app',
        ]
    )


def _exit_with_diagnostics(exc: BaseException) -> None:
    print(_build_startup_help(exc), file=sys.stderr)
    traceback.print_exc()
    raise SystemExit(1) from exc


def run() -> None:
    try:
        from .app import main
    except Exception as exc:  # pragma: no cover - startup diagnostics path
        _exit_with_diagnostics(exc)

    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - runtime diagnostics path
        _exit_with_diagnostics(exc)
