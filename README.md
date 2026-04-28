# Wooden Tetris

当前仓库实现的是一个基于 Python + Pygame 的原木风俄罗斯方块桌面版。

This repository currently contains a desktop Tetris game built with Python and Pygame, styled with a wooden arcade look.

![Wooden Tetris screenshot](./screenshot.png)

## 中文说明

### 当前功能

- 原木自然风格界面，使用暖色木纹面板和街机机柜式布局。
- 标准 7 种俄罗斯方块。
- 下一个方块预览。
- 分数、等级、消行数显示。
- 支持暂停、重新开始和游戏结束覆盖层。
- 支持按键长按连续移动。
- 使用内置字体资源，并在字体不可用时回退到系统字体。
- 包含基础自动化测试和 GitHub Actions CI。

### 环境要求

- Python 3.10+
- Pygame 2.6.1

### 安装

```bash
python -m pip install -r requirements.txt
```

开发和测试环境：

```bash
python -m pip install -e ".[test]"
```

### 运行

推荐方式：

```bash
python main.py
```

也可以：

```bash
python -m tetris_app
```

兼容旧入口：

```bash
python "俄罗斯方块.py"
```

### 操作

- `Left` / `A`：左移
- `Right` / `D`：右移
- `Down` / `S`：加速下落
- `Up` / `W`：旋转
- `Space`：硬降
- `P`：暂停 / 继续
- `R`：重新开始

### 项目结构

```text
.
|-- .github/
|-- assets/
|   `-- fonts/
|-- docs/
|-- main.py
|-- tests/
|-- tetris_app/
|   |-- __main__.py
|   |-- app.py
|   |-- game_state.py
|   |-- launcher.py
|   |-- layout.py
|   |-- pieces.py
|   |-- renderers.py
|   |-- resources.py
|   `-- theme.py
`-- 俄罗斯方块.py
```

### 测试

```bash
python -m py_compile main.py tetris_app/__main__.py
python -m pytest -q
```

定向测试：

```bash
python -m pytest -q tests/test_smoke.py tests/test_input_repeat.py tests/test_game_state.py tests/test_render_smoke.py
```

## English

### Current Features

- Wooden natural UI with a warm palette, wood-grain panels, and an arcade-style cabinet layout.
- Standard 7 tetrominoes.
- Next-piece preview.
- Score, level, and cleared-line counters.
- Pause, restart, and game-over overlays.
- Held-key repeat for movement input.
- Bundled font asset with system-font fallback.
- Basic automated tests and GitHub Actions CI.

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

Recommended:

```bash
python main.py
```

Alternative:

```bash
python -m tetris_app
```

Legacy entrypoint:

```bash
python "俄罗斯方块.py"
```

### Controls

- `Left` / `A`: move left
- `Right` / `D`: move right
- `Down` / `S`: soft drop
- `Up` / `W`: rotate
- `Space`: hard drop
- `P`: pause / resume
- `R`: restart

### Project Structure

```text
.
|-- .github/
|-- assets/
|   `-- fonts/
|-- docs/
|-- main.py
|-- tests/
|-- tetris_app/
|   |-- __main__.py
|   |-- app.py
|   |-- game_state.py
|   |-- launcher.py
|   |-- layout.py
|   |-- pieces.py
|   |-- renderers.py
|   |-- resources.py
|   `-- theme.py
`-- 俄罗斯方块.py
```

### Tests

```bash
python -m py_compile main.py tetris_app/__main__.py
python -m pytest -q
```

Focused tests:

```bash
python -m pytest -q tests/test_smoke.py tests/test_input_repeat.py tests/test_game_state.py tests/test_render_smoke.py
```
