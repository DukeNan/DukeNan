# Repository Guidelines

## Project Structure

This repository generates the DukeNan GitHub profile README. Edit `index.html` for profile text, layout, and image references. `update.py` fetches Shenzhen weather from Open-Meteo and sunrise and sunset times from Sunrise-Sunset, then fills the template and writes `README.md`. Keep profile icons and photos in `images/`. The workflow in `.github/workflows/main.yml` runs `run.sh` every three hours and on pushes to `main`.

## Local Development

Run these commands from the repository root. CI uses Python 3.14, and the updater requires only the standard library.

- `TZ=Asia/Shanghai python3 update.py` regenerates the README using live API data. Use a scratch copy of `update.py` and `index.html` to test generation without changing the tracked README. A run may skip regeneration if the README was already refreshed that day.
- `bash -n run.sh` checks shell syntax without executing the script.
- `git diff --check` checks the patch for whitespace errors.

Use the Python entry point for local validation. `run.sh` is the CI publishing script and uses `git reset --hard` and `git push -f`.

## Coding Style

Use four spaces for Python indentation, `snake_case` for functions and variables, and `UPPER_CASE` for module constants. Match the surrounding indentation in HTML, Bash, and YAML. Keep template placeholders such as `{refresh_date}` in sync with the values supplied by `update.py`. The repository has no configured formatter or linter.

## Testing

The repository has no automated test suite or coverage requirement. After changing the updater or template, generate a fresh README and verify that weather values, local times, and the refresh timestamp render correctly. For layout changes, preview the generated README and check the affected image links.

## Commits and Pull Requests

Use Conventional Commit subjects with an imperative summary, for example `fix(workflow): use Python 3.14 on Ubuntu runners`. In pull requests, describe what changed and how you verified it. Link a related issue when available and include a README preview for visible layout changes.
