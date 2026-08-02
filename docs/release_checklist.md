# Release Checklist

Git stable release tag: `v1.0.0`

Python package version: `1.0.0`

Release-candidate history:

- TestPyPI upload completed for `1.0.0rc1`.
- Fresh TestPyPI install completed for `1.0.0rc1`.
- Release-candidate tag: `v1.0.0-rc1`.

## Pre-release

- Confirm the working tree is clean except intentional release changes.
- Confirm version consistency across `pyproject.toml`, `deriv_sdk/version.py`,
  README, docs, and changelog.
- Compile package, tests, and examples:
  `venv\Scripts\python.exe -m compileall deriv_sdk tests examples`
- Run Ruff format:
  `venv\Scripts\python.exe -m ruff format .`
- Run Ruff format check:
  `venv\Scripts\python.exe -m ruff format --check .`
- Run Ruff lint:
  `venv\Scripts\python.exe -m ruff check .`
- Run MyPy:
  `venv\Scripts\python.exe -m mypy deriv_sdk`
- Run tests:
  `venv\Scripts\python.exe -m pytest -v`
- Remove stale `dist/`, `build/`, and `*.egg-info/` artifacts.
- Build distributions:
  `venv\Scripts\python.exe -m build`
- Run Twine validation:
  `venv\Scripts\python.exe -m twine check dist\*`
- Audit wheel and source distribution contents.
- Install the wheel in a fresh virtual environment.
- Verify public imports:
  `from deriv_sdk import DerivClient, SDKConfig`
- Confirm client construction performs no network operation.
- Compile examples.
- Validate README links and commands.

## Release

- Change `1.0.0rc1` to `1.0.0`. Completed; pending final verification.
- Commit the release.
- Create an annotated `v1.0.0` tag.
- Push the branch and tag.
- Upload to TestPyPI first. Completed for `1.0.0rc1`.
- Install from TestPyPI in a clean environment. Completed for `1.0.0rc1`.
- Upload to PyPI. Not yet completed.
- Create the GitHub Release. Not yet created.

## Post-release

- Install from PyPI in a clean environment.
- Verify the installed version.
- Verify public imports.
- Verify project links on the package index.
- Monitor the issue tracker:
  <https://github.com/Sarahsam01/deriv-python-sdk/issues>
