# Release Checklist

## Automated Validation

- Run `python -m py_compile main.py tetris_app/__main__.py`
- Run `python -m pytest -q`
- Confirm the passing test count includes:
  - smoke bootstrap coverage
  - held-key repeat timing coverage
  - game-state logic coverage
  - renderer smoke coverage

## Manual Validation

- Launch with `python main.py`
- Confirm `python -m tetris_app` starts the same game build
- Verify movement, rotation, soft drop, and hard drop
- Verify pause and resume with `P`
- Verify restart with `R`
- Verify next-piece preview and score / level / lines panels
- Verify pause and game-over overlays remain readable

## Release Assets

- `README.md` matches the shipped file layout and controls
- `screenshot.png` reflects the current wooden natural UI
- `requirements.txt` pins `pygame==2.6.1`
- `pyproject.toml` installs the `tetris_app` package and test extras
- `assets/fonts/` includes the bundled font and license metadata

## GitHub Handoff

- Push the repository with the Phase 1-4 commits intact
- Confirm the GitHub Actions workflow passes on the default branch
- Use the screenshot as the repository social preview or README hero image
- Copy the highlights section from `README.md` into the GitHub release description if needed
