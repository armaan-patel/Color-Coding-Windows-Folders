#!/usr/bin/env python3
"""
Simple system tray helper for Folder Colorizer using pystray.

Provides a small menu: Color a folder, Open GUI, Quit.
"""

from __future__ import annotations

import sys
import subprocess
from pathlib import Path

try:
    import pystray
    from PIL import Image, ImageDraw
except Exception:
    pystray = None
    Image = None
    ImageDraw = None

try:
    import tkinter as tk
    from tkinter import filedialog, colorchooser
except Exception:
    tk = None

import colorize as cz


def _create_icon_image(color: str = '#ffcc00', size: int = 64):
    if Image is None or ImageDraw is None:
        return None
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size, size
    draw.rectangle([ (int(w*0.12), int(h*0.3)), (int(w*0.88), int(h*0.9)) ], fill=color)
    draw.rectangle([ (int(w*0.16), int(h*0.12)), (int(w*0.56), int(h*0.32)) ], fill=color)
    return img


def _open_gui(icon=None, item=None):
    python = sys.executable
    script = str(Path(__file__).parent / 'gui.py')
    subprocess.Popen([python, script])


def _color_a_folder(icon=None, item=None):
    if tk is None:
        print('Tkinter required to pick a folder/color from tray')
        return
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title='Select folder to color')
    if not folder:
        root.destroy()
        return
    c = colorchooser.askcolor(color='#ffcc00', title='Pick color for folder')
    root.destroy()
    if c and c[1]:
        try:
            cz.set_folder_icon(folder, c[1])
        except Exception as e:
            print('Error applying color to folder:', e)


def _quit(icon=None, item=None):
    try:
        icon.stop()
    except Exception:
        pass


def run_tray():
    if pystray is None:
        print('pystray not installed; run pip install -r requirements.txt')
        return
    image = _create_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem('Color a folder...', _color_a_folder),
        pystray.MenuItem('Open GUI', _open_gui),
        pystray.MenuItem('Quit', _quit),
    )
    icon = pystray.Icon('FolderColorizer', image, 'Folder Colorizer', menu)
    icon.run()


def headless_test():
    base = Path(__file__).parent / 'test_output_tray'
    base.mkdir(exist_ok=True)
    fld = base / 'test_tray_folder'
    info = cz.set_folder_icon(str(fld), '#112233')
    print('tray headless test created:', info)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(prog='tray.py')
    parser.add_argument('--test', action='store_true', help='Headless test (does not start tray)')
    args = parser.parse_args()
    if args.test:
        headless_test()
        sys.exit(0)
    run_tray()
