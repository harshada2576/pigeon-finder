This file explains how to contribute code, tests and documentation to Pigeon Finder.

# Contributing

We welcome contributions of all kinds: bug fixes, feature work, tests, documentation and examples.

## Reporting bugs

When filing a bug report, please include:

- A short summary and background
- Steps to reproduce the problem
- What you expected to happen
- What actually happened (including tracebacks if any)
- Your OS and Python version

## Suggesting enhancements

Open a new issue labelled "enhancement" and describe the problem you're trying to solve, why it's beneficial, and an optional implementation plan.

## Making code contributions (Pull Requests)

Follow this workflow:

1. Fork the repository and clone your fork.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Create and activate a project-local virtual environment named `.venv` (example below).
4. Implement your changes and add tests.
5. Run the test suite and linters locally.
6. Commit and push your branch, then open a PR.

Example development setup (Windows PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run tests with pytest:

```powershell
py -3.12 -m pytest -q
```

Commit and push example:

```bash
git add .
git commit -m "feat: short description"
git push origin feature/your-feature
```

Open a pull request on GitHub describing the change and linking any relevant issues.

