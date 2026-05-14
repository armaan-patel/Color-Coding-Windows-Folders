#!/usr/bin/env python3
"""
install_context_menu.py

Creates a per-user (HKCU) context-menu entry for folders that launches
the GUI in quick-pick mode so you can right-click a folder and choose a color.

Usage:
  python install_context_menu.py install
  python install_context_menu.py uninstall
  python install_context_menu.py status

Note: Uses HKCU so no elevation is required.
"""

from __future__ import annotations

import sys
from pathlib import Path

if sys.platform != 'win32':
    print('Context-menu installer is Windows-only')
    sys.exit(1)

import winreg


def get_command_value() -> str:
    python = sys.executable
    script = str(Path(__file__).parent / 'gui.py')
    # %1 will be replaced with the selected folder path
    return f'"{python}" "{script}" --target "%1" --pick'


KEY_BASE = r'Software\Classes\Directory\shell\ColorizeWithFolderColorizer'


def install():
    cmd = get_command_value()
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY_BASE) as k:
            winreg.SetValueEx(k, None, 0, winreg.REG_SZ, 'Color with Folder Colorizer')
            # optional: set a small icon for the menu entry
            # winreg.SetValueEx(k, 'Icon', 0, winreg.REG_SZ, script)
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY_BASE + '\\command') as c:
            winreg.SetValueEx(c, None, 0, winreg.REG_SZ, cmd)
        print('Installed context-menu entry (HKCU\\' + KEY_BASE + ')')
    except Exception as e:
        print('Install failed:', e)


def uninstall():
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, KEY_BASE + '\\command')
    except FileNotFoundError:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, KEY_BASE)
    except FileNotFoundError:
        pass
    print('Uninstalled context-menu entry (if present)')


def status():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_BASE + '\\command', 0, winreg.KEY_READ) as c:
            val, _ = winreg.QueryValueEx(c, None)
            print('Command value:', val)
    except FileNotFoundError:
        print('Context-menu not installed')


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(prog='install_context_menu.py')
    p.add_argument('action', choices=['install', 'uninstall', 'status'], nargs='?', default='status')
    args = p.parse_args()
    if args.action == 'install':
        install()
    elif args.action == 'uninstall':
        uninstall()
    else:
        status()
