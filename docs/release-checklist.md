# Release Checklist

## Automated Validation

- Run `python -m py_compile 俄罗斯方块.py`
- Run `python -m pytest -q`
- Confirm the passing test count includes:
  - smoke bootstrap coverage
  - held-key repeat timing coverage
  - game-state logic coverage
  - renderer smoke coverage

## Manual Validation

- Launch with `python 俄罗斯方块.py`
- Verify movement, rotation, soft drop, and hard drop
- Verify pause and resume with `P`
- Verify restart with `R`
- Verify next-piece preview and score / level / lines panels
- Verify bomb-piece explosion clears the surrounding 8 cells
- Verify pause and game-over overlays remain readable

## Release Assets

- `README.md` matches the shipped file layout and controls
- `screenshot.png` reflects the current neon glass UI
- `requirements.txt` pins `pygame==2.6.1`
- `pyproject.toml` installs the `tetris_app` package and test extras
- `assets/fonts/` includes the bundled font and license metadata

## GitHub Handoff

- Push the repository with the Phase 1-4 commits intact
- Use the screenshot as the repository social preview or README hero image
- Copy the highlights section from `README.md` into the GitHub release description if needed
