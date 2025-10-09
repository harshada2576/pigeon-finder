# First Step Guide — Quick tutorial

This short tutorial shows how to run your first scan with Pigeon Finder on Windows and perform common actions.

## 1) Create and activate a virtual environment

Open PowerShell in the project's root (`C:\Users\Admin\Desktop\clone\pigeon-finder`) and run:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you prefer the quick helper, run:

```powershell
.\quick_setup.ps1
.venv\Scripts\Activate.ps1
```

## 2) Launch the GUI

Run the launcher script (recommended) which starts the PyQt5 application:

```powershell
python .\run_pigeon_finder.py
```

Or run the GUI directly:

```powershell
python pigeon_finder_gui.py
```

## 3) Start a scan

- Choose a folder to scan using the GUI file selector.
- Select file types (or leave empty to scan common types).
- Set minimum size if you want to ignore tiny files.
- Click "Start Scan".

The progress bar and status messages will update. The UI runs scanning in a background thread so the window stays responsive.

## 4) Interpreting results

When the scan finishes, the results table lists detected duplicate groups. Each row shows a canonical (original) file and a list of duplicates.

Actions you can take per group:

- Delete duplicates (moves to recycle bin or permanent delete depending on settings).
- Move duplicates to a chosen folder.
- Export a report (CSV) listing duplicates.

## 5) Troubleshooting quick tips

- If a dependency fails to install on Windows, upgrade pip and setuptools first:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

- For Pillow / PyQt5 build issues, install prebuilt wheels or use the `quick_setup.ps1` which prefers wheels.
- If the GUI doesn't start, check `verify_setup.py` to confirm imports:

```powershell
python verify_setup.py
```

## 6) Next steps

- See `docs/development/api.md` for programmatic usage examples.
- For advanced CLI usage, open `cli/duplicate-finder.py` to see how to call `file_io.scan_files` and `PigeonholeEngine` from scripts.







