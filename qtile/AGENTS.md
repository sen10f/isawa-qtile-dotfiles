# Repository Guidelines

## Project Structure & Module Organization
- `config.py` is the Qtile entrypoint; it wires together colors, keybindings, layouts, widgets, screens, and hooks from `settings/`.
- `settings/` is modular: `colors.py` (palette), `groups.py` (workspaces), `keys.py` (bindings), `layouts.py` (layout defaults + floating rules), `widgets.py` (widget defaults + bar factory), `screens.py` (screen + bar assembly), `hooks.py` (autostart/env). Treat each file as a focused module.
- Supporting scripts live at repo root (e.g., `qtile-menu.sh`, `workspace-preview.py`, `setup.sh` for provisioning) and quick refs in `cheatsheet.txt`. Keep scripts executable and minimal.

## Build, Test, and Development Commands
- `qtile check -l config.py`: quick lint of the config for syntax and common mistakes before reloading.
- `python -m compileall .`: catch syntax errors across `settings/*.py` without restarting the WM.
- `qtile cmd-obj -o cmd -f reload_config`: hot-reload the config after changes; have a terminal ready in case of errors.

## Coding Style & Naming Conventions
- Python 3; use 4-space indentation, snake_case for functions/variables, and UPPER_SNAKE_CASE for constants (e.g., color maps).
- Keep modules small and declarative; prefer data tables (dicts/lists) over ad-hoc logic in `config.py`.
- Match existing patterns when adding bindings or widgets (extend lists in `settings/keys.py` and `settings/widgets.py`).
- Run `qtile check` or `python -m compileall` before reloading to avoid a broken session.

## Testing Guidelines
- Favor targeted checks: adjust or add bindings in `settings/keys.py`, then run `qtile check` and reload.
- For layout/widget tweaks, validate with a temporary test workspace from `groups.py`; ensure bars render and widgets resolve resources/fonts.
- If adding scripts, run them with `shellcheck` when possible and keep them POSIX-sh.

## Commit & Pull Request Guidelines
- Use concise, imperative commit messages ("Add media keys", "Tweak bar widgets"). One logical change per commit.
- In PRs/issues, note modules touched, user-facing changes (bindings, layout defaults, autostart), and reload/test commands you ran.
- Provide screenshots or short notes for visual changes to bars/widgets and mention any new dependencies introduced.

## Security & Configuration Tips
- Avoid embedding secrets or personal tokens in autostart or hooks. Read paths from env vars when needed.
- Keep scripts least-privileged and guarded (exit on error, set safe defaults) to prevent lockups during Qtile start.
