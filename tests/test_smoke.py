import importlib.util
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_launcher_module():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

    launcher = next(ROOT.glob("*.py"))
    spec = importlib.util.spec_from_file_location("tetris_launcher", launcher)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_launcher_imports_and_game_constructs():
    module = load_launcher_module()
    font_path = ROOT / "assets" / "fonts" / "NotoSansSC-Regular.ttf"

    assert callable(module.main)
    assert module.screen.get_size() == (800, 600)
    assert font_path.exists()

    game = module.Game()
    assert game.level == 1
    assert game.lines_cleared == 0
    assert game.score == 0

    font = module.pygame.font.Font(str(font_path), 24)
    surface = font.render("测试", True, (255, 255, 255))
    assert surface.get_width() > 0

    module.pygame.quit()
