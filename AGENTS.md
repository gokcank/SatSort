# SatSort

Linux desktop editor (Python + Qt6/PySide6) for SatcoDX (`.sdx`) satellite channel lists, plus a static landing page in `website/`.

## Build & test
- Setup: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Tests: `python3 -m unittest discover tests` (CI matrix: Python 3.10, 3.11, 3.12). GUI tests need PySide6 installed.
- Syntax check: `python3 -m py_compile $(find satsort scripts -name "*.py")`
- Run: `python3 main.py`
- Packages: `./build_deb.sh` (→ `release_output/`), `./build_appimage.sh`, APT index: `python3 scripts/build_apt_repo.py`
- Release: push a tag `v1.X.X`; `.github/workflows/release.yml` builds `.deb`, AppImage, binary, the GitHub Release and the APT repo.

## Layout
- `satsort/core/` — parser, exporter, models, batch tools, reference sorter, updater, config (no Qt).
- `satsort/ui/` — main window, channel table, sidebar, search bar, theme, `icons.py` (programmatic SVG icons), `dialogs/`.
- `satsort/i18n/translations.json` — one dictionary per language (Türkçe, English, Deutsch, Français, Español), keys `T100`…`T169`.
- `website/` — landing page with an in-browser `.sdx` parser; deployed to `gh-pages` by `deploy-pages.yml`.
- `gh-pages` branch also hosts the APT repository (`pool/`, `dists/`).
- `.sdx` files are git-ignored; tests and screenshots use a local sample list.

## Project rules
- SatcoDX 105 byte/format fidelity is mandatory on parse and export: TV firmware rejects or crashes on malformed files.
- All UI strings go through `t("T…")` with entries in all five languages. No inline `if is_tr else ...` branches in new code.
  New keys take the next free number — check the file first; existing numbers are already used.
- No emojis in the UI or website; use the SVG icon set (`satsort/ui/icons.py`, `website/satsort.svg`).
- `deploy-pages.yml` must keep `keep_files: true`, or website deploys delete the APT repository on `gh-pages`.
- Website screenshots: 1100×700, identical state in every language (sample list loaded, first row selected, right panel open).
- Version bump touches `pyproject.toml`, `satsort/__init__.py`, `CHANGELOG.md` and the fallback in `release.yml`.
- `CHANGELOG.md` is written in Turkish. Commit messages use Conventional Commits (`feat:`, `fix:`, `docs:`, `ci:`, `style:`, `chore:`).
- Work through the terminal (no IDE GUI instructions).

## Status (as of 2026-11-07)
- Project status: **maintenance** (set 2026-11-18; source of truth: the brain page).
- Latest release v1.1.0 (2026-08-29). `main` = `1f37f70`, in sync with origin.
- No virtualenv on this machine yet; tests not run since the OS reinstall.

## Open items
- CI red since 2026-11-07 (last green 2026-08-30): the test step crashes with `Fatal Python error: none_dealloc` (exit 134) in a C extension, on Python 3.10 and 3.11. Commits since then touched only this file, so likely a changed dependency on the runner (unpinned PySide6?); not verified. Investigate in a project session.
- Planned new i18n keys T146–T155 collide with existing keys (e.g. T146, T153): renumber before adding.
- Website ideas (not committed): shortcuts modal, TV setup stepper, PWA, command palette.

## More context
Background, decisions and history are in the second brain: `/home/gokcank/ikinci-beyin/projects/satsort.md` (read on demand).
