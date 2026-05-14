# Color-Coding Windows Folders

This repository contains a small Windows utility to color-code folders by setting custom folder icons.

Structure
- `colorizer/` — main tool and GUI (see `colorizer/README.md` for detailed usage)

Quick start

1. Create and activate the venv (optional but recommended):

```powershell
python -m venv .venv
& "./.venv/Scripts/Activate.ps1"
```

2. Install dependencies:

```powershell
& "./.venv/Scripts/python.exe" -m pip install -r colorizer/requirements.txt
```

3. Run the GUI or tray app:

```powershell
& "./.venv/Scripts/python.exe" colorizer/gui.py
& "./.venv/Scripts/python.exe" colorizer/tray.py
```

Repository: https://github.com/armaan-patel/Color-Coding-Windows-Folders.git

# Author:
Armaan Patel
B.S. Computer Science, DeSales University
Incoming NYU Stern MBA

License: MIT
