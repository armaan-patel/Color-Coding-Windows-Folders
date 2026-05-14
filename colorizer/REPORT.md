# Color Folderizer — Report

**Summary:** Implemented a small Windows utility that color-codes folders by creating a colored `.ico` and a `desktop.ini` inside target folders so Explorer shows a colored folder icon.

- **Script:** [colorizer/colorize.py](colorizer/colorize.py)
- **README:** [colorizer/README.md](colorizer/README.md)
- **Dependencies:** `Pillow` (see [colorizer/requirements.txt](colorizer/requirements.txt))

**What I implemented**
- Generates simple folder-shaped `.ico` files in a package-local `.folder_icons` directory.
- Copies the icon into the target folder, writes a `desktop.ini` with `IconFile=...` and sets folder attributes so Explorer will use the icon (Windows only).
- CLI commands: `set`, `remove`, `list` and a `--test` self-test mode that creates sample colored folders under the package folder.

**Self-test results**

The script's self-test created sample folders and desktop.ini files. Excerpt from the test report:

```
Folder: colorizer/test_output/test_4444ff
[.ShellClassInfo]
IconFile=icon_4444ff.ico
IconIndex=0

Folder: colorizer/test_output/test_44ff44
[.ShellClassInfo]
IconFile=icon_44ff44.ico
IconIndex=0

Folder: colorizer/test_output/test_ff4444
[.ShellClassInfo]
IconFile=icon_ff4444.ico
IconIndex=0

Folder: colorizer/test_output/test_orange
[.ShellClassInfo]
IconFile=icon_orange.ico
IconIndex=0

Folder: colorizer/test_output/test_purple
[.ShellClassInfo]
IconFile=icon_purple.ico
IconIndex=0
```

Files written by the test are under: `colorizer/test_output/` and a short report file was written at `colorizer/test_report.txt`.

**How to run**
- Use the venv Python created in the workspace. Example command (PowerShell):

```
& "./.venv/Scripts/python.exe" -m pip install -r colorizer/requirements.txt
& "./.venv/Scripts/python.exe" colorizer/colorize.py set "C:\Path\To\Folder" --color "#ff8800"
```

**Notes & next steps**
- This approach colors folders (not individual file icons). Per-file coloring in Explorer requires a shell extension or converting files to shortcuts with custom icons — more complex and beyond this small tool.
- If you want a GUI, per-file tagging, or Explorer integration (overlay icons), I can extend this into a small GUI or write a shell extension — tell me which direction you prefer.

**GUI Added**

- Implemented a Tkinter GUI at `colorizer/gui.py` that lets you add folders, pick a color and apply/remove folder icons interactively.
- Headless GUI test run created: `colorizer/test_output_gui/test_gui_folder` with `desktop.ini` and `icon_00ccff.ico`.
- How to run GUI (PowerShell):

```
& "./.venv/Scripts/python.exe" colorizer/gui.py
```

Headless test:

```
& "./.venv/Scripts/python.exe" colorizer/gui.py --test
```

The GUI uses the same `set_folder_icon` and `remove_folder_icon` logic from `colorize.py` so behavior is identical to the CLI.

**Tray & Context Menu**

- Added a small system tray helper at `colorizer/tray.py` to quickly color a folder or open the GUI.
- Added a per-user context-menu installer `colorizer/install_context_menu.py` which creates a right-click item for folders that launches the GUI in quick-pick mode (no elevation required; writes under `HKCU`).
- Example install command (PowerShell):

```
& "./.venv/Scripts/python.exe" colorizer/install_context_menu.py install
```

Headless tray test:

```
& "./.venv/Scripts/python.exe" colorizer/tray.py --test
```

These additions let you right-click a folder and immediately pick a color for it using the GUI's color chooser.

**Desktop shortcut**

- Added `colorizer/create_desktop_shortcut.py` which can create a Desktop shortcut named `Folder Colorizer (Tray)` that launches the tray app (uses `pythonw` if available).
- I ran the helper and created `Folder Colorizer (Tray).lnk` on your Desktop.

Create/remove/status commands:

```
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py create
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py remove
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py status
```

