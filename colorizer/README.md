# Folder Colorizer

This small tool sets a custom colored folder icon on Windows by creating a `desktop.ini` and an `.ico` file inside the folder.

Features
- Generate simple colored folder icons (Pillow)
- Apply `desktop.ini` and set necessary attributes (Windows `attrib`)
- Remove applied icons
- Self-test that creates sample colored folders under the package folder

Usage examples

- Set a folder icon:

```
python colorize.py set "C:\path\to\folder" --color "#ff8800"
```

- Remove the custom icon from a folder:

```
python colorize.py remove "C:\path\to\folder"
```

- Run the built-in self-test (creates `test_output` next to the script):

```
python colorize.py --test
```

Notes
- This modifies folder attributes and places a small `.ico` and `desktop.ini` in folders; it is Windows-only for full effect.
- The script avoids touching your existing folders during the self-test by creating a `test_output` folder inside the package directory.

GUI
---

A small Tkinter GUI is included as `gui.py` for interactive usage. To run the GUI (PowerShell example):

```
& "./.venv/Scripts/python.exe" colorizer/gui.py
```

Headless test for the GUI:

```
& "./.venv/Scripts/python.exe" colorizer/gui.py --test
```

Use the GUI to add folders, pick a color, and press `Apply Color` to set the folder icon.

Tray app
---

A lightweight system tray helper is included as `tray.py`. It provides a small menu with:

- `Color a folder...` — choose a folder and color quickly from the tray
- `Open GUI` — open the full Tkinter GUI
- `Quit` — exit the tray app

Run the tray app (PowerShell):

```
& "./.venv/Scripts/python.exe" colorizer/tray.py
```

Context-menu (Right-click)
---

You can add a per-user context-menu entry so that when you right-click any folder you can choose `Color with Folder Colorizer` and immediately pick a color. Install it with:

```
& "./.venv/Scripts/python.exe" colorizer/install_context_menu.py install
```

To remove the context-menu entry:

```
& "./.venv/Scripts/python.exe" colorizer/install_context_menu.py uninstall
```

Check status:

```
& "./.venv/Scripts/python.exe" colorizer/install_context_menu.py status
```

The installer writes into `HKCU\Software\Classes\Directory\shell` (per-user), so no elevation is required.

Desktop shortcut
---

You can create a Desktop shortcut that starts the tray app (uses `pythonw` when available to avoid a console). The helper is `create_desktop_shortcut.py`.

Create the shortcut:

```
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py create
```

Remove the shortcut:

```
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py remove
```

Check status:

```
& "./.venv/Scripts/python.exe" colorizer/create_desktop_shortcut.py status
```

When I ran the creation helper it created `Folder Colorizer (Tray).lnk` on your Desktop.
