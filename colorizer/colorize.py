#!/usr/bin/env python3
"""
colorize.py - Color-code Windows folders by setting custom folder icons via desktop.ini

This script generates small .ico files with a simple folder-like shape filled
with the requested color, writes a `desktop.ini` in the target folder that
references the icon, and sets the necessary Windows attributes so Explorer
displays the custom icon.

Run `python colorize.py --help` for usage.
"""

from __future__ import annotations

import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except Exception:
    Image = None
    ImageDraw = None
    ImageFilter = None

def ensure_icons_dir(base_dir: Path) -> Path:
    icons_dir = Path(base_dir) / ".folder_icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    return icons_dir

def parse_color(s: str):
    s = str(s).strip()
    if s.startswith('#'):
        hexv = s.lstrip('#')
        if len(hexv) == 3:
            hexv = ''.join([c*2 for c in hexv])
        if len(hexv) != 6:
            raise ValueError(f"Invalid hex color: {s}")
        r = int(hexv[0:2], 16)
        g = int(hexv[2:4], 16)
        b = int(hexv[4:6], 16)
        return (r, g, b, 255)
    named = {
        'red': (220,20,60,255), 'green': (60,179,113,255), 'blue': (65,105,225,255),
        'yellow': (255,215,0,255), 'orange':(255,140,0,255),'purple':(128,0,128,255),
        'pink':(255,105,180,255),'gray':(128,128,128,255),'black':(0,0,0,255),'white':(255,255,255,255)
    }
    key = s.lower()
    if key in named:
        return named[key]
    raise ValueError(f"Unknown color: {s}")

def generate_folder_icon(rgba, out_path: str, size: int = 256):
    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow is required. Run: pip install -r requirements.txt")
    # Create base images
    w = h = size
    base = Image.new('RGBA', (w, h), (0, 0, 0, 0))

    # compute geometry
    margin = int(w * 0.06)
    tab_h = int(h * 0.20)
    body_y = int(h * 0.30)
    tab_w = int(w * 0.44)
    tab_x = margin * 2

    # Prepare a mask for the folder shape
    mask = Image.new('L', (w, h), 0)
    md = ImageDraw.Draw(mask)
    # rounded rectangles for tab and body
    radius = max(4, int(size * 0.06))
    md.rounded_rectangle([ (tab_x, margin), (tab_x + tab_w, margin + tab_h) ], radius=radius, fill=255)
    md.rounded_rectangle([ (margin, body_y), (w - margin, h - margin) ], radius=radius, fill=255)

    # Create top-to-bottom gradient based on the provided color
    r, g, b, a = rgba
    # lighter and darker variants
    def clamp(x):
        return max(0, min(255, int(x)))
    lighter = (clamp(r + 30), clamp(g + 30), clamp(b + 30), a)
    darker = (clamp(r - 20), clamp(g - 20), clamp(b - 20), a)

    grad = Image.new('RGBA', (w, h), (0,0,0,0))
    for y in range(h):
        t = y / (h - 1)
        rr = int(lighter[0] * (1 - t) + darker[0] * t)
        gg = int(lighter[1] * (1 - t) + darker[1] * t)
        bb = int(lighter[2] * (1 - t) + darker[2] * t)
        grad.paste((rr, gg, bb, a), [0, y, w, y+1])

    # apply gradient into folder mask
    base.paste(grad, (0,0), mask)

    draw = ImageDraw.Draw(base)

    # subtle border
    border_mask = mask.copy()
    if ImageFilter is not None:
        border_mask = border_mask.filter(ImageFilter.GaussianBlur(max(1, int(size*0.005))))
    edge = Image.new('RGBA', (w, h), (0,0,0,0))
    ed = ImageDraw.Draw(edge)
    ed.bitmap((0,0), border_mask, fill=(0,0,0,40))
    base = Image.alpha_composite(edge, base)

    # add a small glossy highlight on the folder body
    gloss = Image.new('RGBA', (w, h), (0,0,0,0))
    gd = ImageDraw.Draw(gloss)
    gloss_h = int(h * 0.18)
    gd.ellipse([ (margin, body_y - gloss_h//2), (w - margin, body_y + gloss_h) ], fill=(255,255,255,80))
    if ImageFilter is not None:
        gloss = gloss.filter(ImageFilter.GaussianBlur(int(size*0.01)))
    base = Image.alpha_composite(base, gloss)

    # draw a subtle drop shadow below the folder
    if ImageFilter is not None:
        shadow = mask.copy().convert('L')
        shadow = shadow.filter(ImageFilter.GaussianBlur(int(size*0.02)))
        sh = Image.new('RGBA', (w, h), (0,0,0,0))
        sd = ImageDraw.Draw(sh)
        sd.bitmap((0, int(size*0.01)), shadow, fill=(0,0,0,80))
        base = Image.alpha_composite(sh, base)

    # Save as ICO with multiple sizes for Explorer
    sizes = [(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)]
    base.save(out_path, format='ICO', sizes=sizes)

def write_desktop_ini(folder_path: Path, icon_filename: str) -> Path:
    desktop_ini = folder_path / 'desktop.ini'
    content = f"[.ShellClassInfo]\nIconFile={icon_filename}\nIconIndex=0\n"
    try:
        # On Windows, try to clear attributes (hidden/system/read-only) before writing
        if os.name == 'nt' and desktop_ini.exists():
            try:
                import ctypes
                FILE_ATTRIBUTE_NORMAL = 0x80
                ctypes.windll.kernel32.SetFileAttributesW(str(desktop_ini), FILE_ATTRIBUTE_NORMAL)
            except Exception:
                pass
        desktop_ini.write_text(content, encoding='utf-8')
    except PermissionError:
        # Fallback: write to a temp file then replace
        tmp = folder_path / 'desktop.ini.new'
        tmp.write_text(content, encoding='utf-8')
        try:
            os.replace(str(tmp), str(desktop_ini))
        except Exception:
            # re-raise original PermissionError if replacement fails
            raise
    return desktop_ini

def set_windows_attributes(folder_path: str, desktop_ini_path: str):
    if os.name != 'nt':
        print('Non-Windows platform: skipping attrib operations')
        return
    try:
        subprocess.run(f'attrib +s "{folder_path}"', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Warning: failed to set folder system attribute')
    try:
        subprocess.run(f'attrib +h +s "{desktop_ini_path}"', shell=True, check=True)
    except subprocess.CalledProcessError:
        print('Warning: failed to set desktop.ini attributes')

def set_folder_icon(folder_path: str, color: str, base_dir: str | Path | None = None):
    folder = Path(folder_path)
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)
    base = Path(base_dir) if base_dir is not None else Path(__file__).parent
    icons_dir = ensure_icons_dir(base)
    safe_color = color.strip().lstrip('#').replace(' ', '_').lower()
    icon_name = f'icon_{safe_color}.ico'
    icon_src = icons_dir / icon_name
    if not icon_src.exists():
        rgba = parse_color(color)
        generate_folder_icon(rgba, str(icon_src))
    icon_dst = folder / icon_name
    try:
        shutil.copyfile(str(icon_src), str(icon_dst))
    except Exception:
        # continue even if copy fails
        pass
    desktop_ini = write_desktop_ini(folder, icon_name)
    set_windows_attributes(str(folder), str(desktop_ini))
    return { 'folder': str(folder), 'icon': str(icon_dst), 'desktop_ini': str(desktop_ini) }

def remove_folder_icon(folder_path: str) -> list:
    folder = Path(folder_path)
    desktop_ini = folder / 'desktop.ini'
    removed = []
    if desktop_ini.exists():
        txt = desktop_ini.read_text(encoding='utf-8')
        icon_name = None
        for line in txt.splitlines():
            if line.strip().lower().startswith('iconfile'):
                parts = line.split('=', 1)
                if len(parts) > 1:
                    icon_name = parts[1].strip()
                    break
        try:
            desktop_ini.unlink()
            removed.append(str(desktop_ini))
        except Exception:
            pass
        if icon_name:
            icon_file = folder / icon_name
            if icon_file.exists():
                try:
                    icon_file.unlink()
                    removed.append(str(icon_file))
                except Exception:
                    pass
    return removed

def find_colored_folders(root: str) -> list:
    root = Path(root)
    found = []
    for p in root.rglob('desktop.ini'):
        found.append((str(p.parent), p.read_text(encoding='utf-8')))
    return found

def run_test(out_root: Path):
    base = Path(out_root)
    base.mkdir(parents=True, exist_ok=True)
    colors = ['#ff4444', '#44ff44', '#4444ff', 'orange', 'purple']
    created = []
    for c in colors:
        fld = base / f'test_{c.strip("#")}'
        info = set_folder_icon(str(fld), c, base_dir=Path(__file__).parent)
        created.append(info)
        print('Created:', info)
    found = find_colored_folders(base)
    report_lines = []
    for f, txt in found:
        report_lines.append(f'Folder: {f}\n{txt}\n')
    report = '\n'.join(report_lines)
    rep_file = Path(__file__).parent / 'test_report.txt'
    rep_file.write_text(report, encoding='utf-8')
    print('Self-test complete. Report:', rep_file)
    return { 'created': created, 'report': str(rep_file) }

def main():
    parser = argparse.ArgumentParser(description='Colorize Windows folders via desktop.ini')
    sub = parser.add_subparsers(dest='cmd')
    p_set = sub.add_parser('set', help='Set a folder icon')
    p_set.add_argument('folder')
    p_set.add_argument('--color', '-c', default='yellow')
    p_rm = sub.add_parser('remove', help='Remove a custom icon from a folder')
    p_rm.add_argument('folder')
    p_list = sub.add_parser('list', help='List colored folders under a root')
    p_list.add_argument('root', nargs='?', default='.')
    parser.add_argument('--test', action='store_true', help='Run self-test (creates test_output)')
    args = parser.parse_args()
    if args.test:
        run_test(Path(__file__).parent / 'test_output')
        return
    if args.cmd == 'set':
        info = set_folder_icon(args.folder, args.color)
        print('Done:', info)
    elif args.cmd == 'remove':
        removed = remove_folder_icon(args.folder)
        print('Removed:', removed)
    elif args.cmd == 'list':
        for f, txt in find_colored_folders(args.root):
            print(f)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
