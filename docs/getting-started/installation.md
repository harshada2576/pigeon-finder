
# Installation

This guide shows how to set up Pigeon Finder locally for development and use.

## Prerequisites

- Python 3.12 (recommended)
- pip
- Git (optional, for cloning the repository)

## Quick setup (Windows PowerShell)

The repository includes a helper script that creates a project-local virtual environment (`.venv`) and installs requirements.

```powershell
git clone https://github.com/your-username/pigeon-finder.git
cd pigeon-finder
.\quick_setup.ps1
```

After the script completes, activate the environment and run the GUI:

```powershell
.venv\Scripts\Activate.ps1
python pigeon_finder_gui.py
```

## Manual setup (alternative)

If you prefer to set up manually:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If a package fails to build (Windows), see `docs/troubleshooting.md` for guidance on prebuilt wheels and build tools.

## Verify installation

Run the verify script to confirm critical imports are available:

```powershell
python verify_setup.py
```








