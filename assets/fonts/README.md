# Font Assets

## NotoSansSC-Regular.ttf

- Family: Noto Sans SC
- Intended usage: bundled Chinese-capable UI font for the Tetris sidebar, overlays, and title text
- Local filename: `NotoSansSC-Regular.ttf`
- Source mirror used in this repository: `https://github.com/jsntn/webfonts/blob/master/NotoSansSC-Regular.ttf`
- Original upstream family and license source: Noto CJK Sans project from `notofonts/noto-cjk`
- Upstream license file copied into this directory as `OFL.txt`

## Notes

- The project bundles the font so GitHub users do not depend on Windows-specific system fonts for correct Chinese glyph rendering.
- Later runtime code should resolve this bundled asset first and only fall back to system fonts if the asset is unavailable.
