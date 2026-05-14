#!/usr/bin/env python3
"""
create_desktop_shortcut.py

Create / remove a Desktop shortcut that launches the Folder Colorizer tray app.

Usage:
  python create_desktop_shortcut.py create
  python create_desktop_shortcut.py remove
  python create_desktop_shortcut.py status

The script uses the current Python executable (prefers pythonw.exe if available)
so the tray runs without a console window.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from win32com.shell import shell, shellcon
    from win32com.client import Dispatch
except Exception as e:
    print('pywin32 is required (pip install pywin32)')
    raise


def _desktop_path() -> str:
    return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)


def create_shortcut(name: str = 'Folder Colorizer (Tray)', script: str | None = None, use_pythonw: bool = True) -> str:
    if script is None:
        script = str(Path(__file__).parent / 'tray.py')
    python_exe = sys.executable
    if use_pythonw:
        pythonw = Path(python_exe).with_name('pythonw.exe')
        target = str(pythonw) if pythonw.exists() else python_exe
    else:
        target = python_exe

    desktop = _desktop_path()
    link_path = Path(desktop) / f'{name}.lnk'
    wsh = Dispatch('WScript.Shell')
    shortcut = wsh.CreateShortcut(str(link_path))
    shortcut.TargetPath = target
    shortcut.Arguments = f'"{script}"'
    shortcut.WorkingDirectory = str(Path(script).parent)
    shortcut.IconLocation = target
    shortcut.Save()
    return str(link_path)


def remove_shortcut(name: str = 'Folder Colorizer (Tray)') -> bool:
    desktop = _desktop_path()
    link = Path(desktop) / f'{name}.lnk'
    if link.exists():
        link.unlink()
        return True
    return False


def status_shortcut(name: str = 'Folder Colorizer (Tray)') -> str:
    desktop = _desktop_path()
    link = Path(desktop) / f'{name}.lnk'
    return str(link) if link.exists() else ''


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(prog='create_desktop_shortcut.py')
    p.add_argument('action', choices=['create', 'remove', 'status'], nargs='?', default='create')
    p.add_argument('--name', default='Folder Colorizer (Tray)')
    p.add_argument('--script', default=str(Path(__file__).parent / 'tray.py'))
    p.add_argument('--no-pythonw', dest='pythonw', action='store_false')
    args = p.parse_args()
    if args.action == 'create':
        link = create_shortcut(name=args.name, script=args.script, use_pythonw=args.pythonw)
        print('Created shortcut:', link)
    elif args.action == 'remove':
        ok = remove_shortcut(name=args.name)
        print('Removed' if ok else 'Not found')
    else:
        s = status_shortcut(name=args.name)
        print('Exists:' if s else 'Not found', s)
