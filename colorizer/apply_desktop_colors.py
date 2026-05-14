#!/usr/bin/env python3
"""
Apply requested color mapping to Desktop folders.

Column mapping (as requested):
- Column 1 (purple): first 4 folders
- Column 2 (green): next 4 folders
- Column 3 (blue): next 4 folders
- Column 4 (plain): remaining folders (remove custom icon)

This script targets the specific folder names discovered on your Desktop.
"""

from pathlib import Path
import sys

try:
    from win32com.shell import shell, shellcon
except Exception:
    shell = None

def get_desktop_path():
    try:
        if shell is not None:
            p = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
            return Path(p)
    except Exception:
        pass
    return Path.home() / 'Desktop'


def main():
    desktop = get_desktop_path()
    print('Desktop path:', desktop)
    # Expected folder ordering discovered earlier
    col1 = [
        "AI Capabilities Testing Ground",
        "Fleetbase Test Files",
        "Logistic Routing Tool HTML Copies",
        "Logistic Software MY TESTING FIles",
    ]
    col2 = [
        "Logistic Software Package for Jake",
        "Logistic Software Windows Development",
        "Logistic Software Working Copies",
        "Logistics ChatGPT Test Files",
    ]
    col3 = [
        "ollama-ipex-llm-2.2.0-win",
        "php-8.5.3-Win32-vs17-x64",
        "Project Status Report",
        "Temp Holder for Yard Images",
    ]
    col4 = [
        "windows-native",
    ]

    # colors (avoiding red/orange/yellow)
    PURPLE = '#7c3aed'
    GREEN = '#2fbf7a'
    BLUE = '#3b82f6'
    DEFAULT = '#0ea5a4'

    try:
        import colorize as cz
    except Exception:
        # try loading by path
        import importlib.util
        p = Path(__file__).parent / 'colorize.py'
        spec = importlib.util.spec_from_file_location('colorize', str(p))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cz = module

    results = []

    def apply_list(lst, color=None, remove=False):
        for name in lst:
            folder = desktop / name
            if not folder.exists() or not folder.is_dir():
                print('Not found (skipping):', folder)
                results.append((str(folder), 'missing'))
                continue
            try:
                if remove:
                    removed = cz.remove_folder_icon(str(folder))
                    print('Removed for', name, removed)
                    results.append((str(folder), 'removed', removed))
                else:
                    c = color if color is not None else DEFAULT
                    info = cz.set_folder_icon(str(folder), c)
                    print('Applied', c, '->', name)
                    results.append((str(folder), 'applied', c))
            except Exception as e:
                print('Error for', name, e)
                results.append((str(folder), 'error', str(e)))

    apply_list(col1, color=PURPLE)
    apply_list(col2, color=GREEN)
    apply_list(col3, color=BLUE)
    apply_list(col4, remove=True)

    # If there are any other folders on the Desktop not in the lists, color them DEFAULT (safe teal)
    all_listed = set(col1 + col2 + col3 + col4)
    for p in desktop.iterdir():
        if p.is_dir() and p.name not in all_listed:
            try:
                info = cz.set_folder_icon(str(p), DEFAULT)
                print('Applied default to', p.name)
                results.append((str(p), 'applied', DEFAULT))
            except Exception as e:
                print('Error default', p.name, e)
                results.append((str(p), 'error', str(e)))

    print('\nSummary:')
    for r in results:
        print(r)

if __name__ == '__main__':
    main()
