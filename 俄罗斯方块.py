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
            "Then launch again with:",
            f'"{sys.executable}" "俄罗斯方块.py"',
        ]
    )


try:
    from tetris_app.app import main
except Exception as exc:  # pragma: no cover - startup diagnostics path
    print(_build_startup_help(exc), file=sys.stderr)
    traceback.print_exc()
    raise SystemExit(1) from exc


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - runtime diagnostics path
        print(_build_startup_help(exc), file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1) from exc
