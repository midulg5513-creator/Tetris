import importlib.util
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FONT_PATH = ROOT / "assets" / "fonts" / "NotoSansSC-Regular.ttf"


def load_launcher_module():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    launcher = ROOT / "main.py"
    spec = importlib.util.spec_from_file_location("tetris_launcher", launcher)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_launcher_import_is_side_effect_free_and_bootstrap_runs():
    module = load_launcher_module()
    from tetris_app import app

    assert callable(module.main)
    assert not app.pygame.display.get_init()
    assert FONT_PATH.exists()
    assert module.main(max_frames=1) == 0

    app.pygame.font.init()
    font = app.pygame.font.Font(str(FONT_PATH), 24)
    surface = font.render("Test", True, (255, 255, 255))
    assert surface.get_width() > 0

    app.pygame.quit()
