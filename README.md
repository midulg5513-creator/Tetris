# Neon Glass Tetris

A polished Pygame Tetris release with a neon sci-fi look, bright glassmorphism panels, bundled font assets, and a modular runtime that is ready to publish on GitHub.

![Neon Glass Tetris screenshot](./screenshot.png)

## Highlights

- Explicit bootstrap path: importing the launcher no longer opens a Pygame window.
- Modular architecture: runtime, game state, pieces, theme, layout, and renderer layers are split cleanly.
- Neon glass UI: bright translucent cards, glowing blocks, and overlay states built for release presentation.
- Bomb block mechanic: special bomb pieces clear the 8 surrounding cells.
- Bundled typography: the repo ships with `assets/fonts/NotoSansSC-Regular.ttf` and license metadata.
- Headless regression coverage: smoke, input timing, game-state, and render-smoke tests run under dummy SDL.

## Quick Start

### Requirements

- Python 3.10+
- Pygame 2.6.1

### Install

```bash
python -m pip install -r requirements.txt
```

For development and tests:

```bash
python -m pip install -e ".[test]"
```

### Run

```bash
python 俄罗斯方块.py
```

## Controls

- `A` / `D`: move left or right
- `W`: rotate
- `S`: soft drop
- `Space`: hard drop
- `P`: pause / resume
- `R`: restart

## Project Structure

```text
.
|-- 俄罗斯方块.py
|-- assets/
|   `-- fonts/
|-- docs/
|-- tests/
`-- tetris_app/
    |-- app.py
    |-- game_state.py
    |-- layout.py
    |-- pieces.py
    |-- renderers.py
    |-- resources.py
    `-- theme.py
```

## Test Commands

```bash
python -m pytest -q
```

Focused validation:

```bash
python -m pytest -q tests/test_smoke.py tests/test_input_repeat.py tests/test_game_state.py tests/test_render_smoke.py
```

## Release Notes

- The launcher stays simple for end users, while the actual runtime lives in `tetris_app`.
- The repo includes a release checklist in [`docs/release-checklist.md`](./docs/release-checklist.md).
- Font licensing details live in `assets/fonts/README.md` and `assets/fonts/OFL.txt`.
