# Contributing

We welcome contributions! This document provides guidelines for contributing to this project.

## Submitting Bugs

### Before Submitting

Before submitting a bug report, please do the following:

- **Make sure you're on the latest version.** Your problem may have been solved already.
- **Try older versions.** If you're on the latest release, try rolling back a few minor versions to help narrow down when the problem first arose.
- **Try switching up dependency versions.** Try upgrading/downgrading dependencies as well.
- **Search the project's issue tracker** to make sure it's not a known issue.
- **Check with the community** in case the problem is non-bug-related.

### Bug Report Contents

Make sure your report includes:

- **Operating system:** Windows? macOS? Linux? Include version details (e.g., Windows 11 64-bit, macOS Ventura 13.6, Ubuntu 22.04).
- **Programming language version:** Include the interpreter/compiler version (e.g., Python 3.11.4). This project requires Python 3.9 or higher.
- **Software version:** Which version(s) of the software are you using?
- **Installation method:** How did you install the runtime and software? (OS packages, pyenv, from source, Conda, virtualenv, etc.)
- **Steps to reproduce:** Include a copy of your code, the command you used, and the full output. Try to pare down your code to a simple "base case" that still reproduces the bug.

## Contributing Changes

### Licensing

By contributing to this project, you agree that your contributions will be licensed under the same terms as the rest of the project (see the `LICENSE` file in the repository root).

- Per-file copyright/license headers are typically not needed. Please don't add your own copyright headers to new files unless the project's license actually requires them.

### Version Control

- **Always make a new branch** for your work, no matter how small.
- **Don't submit unrelated changes in the same branch/pull request.**
- **Base your branch appropriately:**
  - **Bug fixes** should be based on the branch named after the **oldest supported release line** the bug affects.
  - **New features** should branch off of **the main branch**.
  - If your PR has been sidelined for a while, **rebase or merge to latest main** before resubmitting.

### Code Formatting

- **Follow the style you see used in the primary repository.** Consistency with the rest of the project always trumps other considerations.
- For Python projects, follow PEP-8 guidelines (with any project-specific deviations).

### Documentation

Documentation is required for all contributions:

- **Docstrings/API documentation** must be created or updated for public API functions/methods/etc.
  - For Python, include `versionadded` or `versionchanged` directives in docstrings when applicable.
- **Prose documentation** should be updated for new features, including useful example code snippets.
- **Changelog entry** should credit the contributor and any individuals instrumental in identifying the problem.

### Tests

Tests are required for all contributions:

- **Bug fixes** must include a test proving the existence of the bug being fixed.
- **New features** must include tests proving they actually work.
- Writing tests before the implementation is strongly encouraged (test-first development).
- This project uses **pytest** for testing. Run tests with `pytest` or `python -m pytest`.
- Test configuration is in `pyproject.toml`.

## Workflow Example

Here's an example workflow for contributing:

### Preparing Your Fork

1. Fork the repository on GitHub.
2. Clone your fork: `git clone git@github.com:yourname/htseq-count-cluster.git`
3. `cd htseq-count-cluster`
4. Create and activate a virtual environment: `python -m venv venv` (Python 3.9+ required).
5. Install the package in editable mode with development dependencies: `pip install -e ".[dev]"`
6. Create a branch: `git checkout -b fix-description main` (or appropriate base branch).

### Making Your Changes

1. Add a changelog entry crediting yourself.
2. Write tests expecting the correct/fixed functionality; make sure they fail initially.
3. Implement your changes.
4. Run tests: `pytest` or `python -m pytest` (use `pytest -v` for verbose output).
5. Update documentation as needed.
6. Commit your changes: `git commit -m "Brief description of changes"`

### Creating Pull Requests

1. Push your branch: `git push origin HEAD`
2. Visit GitHub and click the "Pull request" button.
3. In the description field, reference the issue number (if fixing an existing issue) or describe the issue and your fix.
4. Submit and be patient - maintainers will review when they can.

## Questions?

If you have questions about contributing, please open an issue or contact the maintainers.