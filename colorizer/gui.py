#!/usr/bin/env python3
"""
Simple Tkinter GUI for the folder colorizer.

Allows you to add folders, pick a color, and apply/remove the custom folder icon.
Also provides a headless `--test` mode for automated verification.
"""

from __future__ import annotations

import argparse
import importlib.util
import threading
import sys
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import filedialog, colorchooser, messagebox
except Exception:
    tk = None


def load_colorize_module():
    try:
        import colorize as cz
        return cz
    except Exception:
        spec = importlib.util.spec_from_file_location(
            'colorize', str(Path(__file__).parent / 'colorize.py')
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


colorize = load_colorize_module()
set_folder_icon = getattr(colorize, 'set_folder_icon')
remove_folder_icon = getattr(colorize, 'remove_folder_icon')


class App:
    def __init__(self, root: 'tk.Tk'):
        if tk is None:
            raise RuntimeError('Tkinter not available in this Python build.')
        self.root = root
        root.title('Folder Colorizer (GUI)')
        self.color_hex = '#ffcc00'

        left = tk.Frame(root)
        right = tk.Frame(root)
        left.pack(side='left', fill='both', expand=True, padx=8, pady=8)
        right.pack(side='right', fill='y', padx=8, pady=8)

        tk.Label(left, text='Folders to color:').pack(anchor='nw')
        self.listbox = tk.Listbox(left, selectmode='extended')
        self.listbox.pack(fill='both', expand=True, side='left')
        sb = tk.Scrollbar(left, orient='vertical', command=self.listbox.yview)
        sb.pack(side='left', fill='y')
        self.listbox.config(yscrollcommand=sb.set)
        self.folders: list[str] = []

        tk.Button(right, text='Add Folder', width=18, command=self.add_folder).pack(pady=3)
        tk.Button(right, text='Remove Selected', width=18, command=self.remove_selected).pack(pady=3)
        tk.Label(right, text='Selected Color:').pack(pady=(12, 0))
        self.color_preview = tk.Label(right, bg=self.color_hex, width=18, height=2, relief='sunken')
        self.color_preview.pack(pady=3)
        tk.Button(right, text='Pick Color', width=18, command=self.pick_color).pack(pady=3)
        tk.Button(right, text='Apply Color', width=18, command=self.apply_color).pack(pady=(12, 3))
        tk.Button(right, text='Remove Color', width=18, command=self.remove_color).pack(pady=3)
        tk.Button(right, text='Self-Test', width=18, command=self.self_test).pack(pady=(12, 3))
        tk.Button(right, text='Quit', width=18, command=root.quit).pack(pady=(30, 3))

        tk.Label(left, text='Log:').pack(anchor='nw')
        self.log_text = tk.Text(left, height=8, state='disabled', wrap='word')
        self.log_text.pack(fill='x', expand=False, pady=(4, 0))

    def add_folder(self):
        path = filedialog.askdirectory(title='Select folder to color')
        if not path:
            return
        if path in self.folders:
            self.log(f'Already added: {path}')
            return
        self.folders.append(path)
        self.listbox.insert('end', path)
        self.log(f'Added: {path}')

    def remove_selected(self):
        sels = list(self.listbox.curselection())
        if not sels:
            return
        for idx in reversed(sels):
            self.log(f'Removed from list: {self.folders[idx]}')
            self.listbox.delete(idx)
            del self.folders[idx]

    def pick_color(self):
        c = colorchooser.askcolor(color=self.color_hex, title='Pick a color')
        if c and c[1]:
            self.color_hex = c[1]
            self.color_preview.config(bg=self.color_hex)
            self.log(f'Picked color: {self.color_hex}')

    def apply_color(self):
        sels = list(self.listbox.curselection())
        if not sels:
            messagebox.showinfo('No folder', 'Select one or more folders to apply color.')
            return
        folders = [self.folders[i] for i in sels]
        t = threading.Thread(target=self._apply_worker, args=(folders, self.color_hex), daemon=True)
        t.start()

    def _apply_worker(self, folders: list[str], color: str):
        for f in folders:
            try:
                self.log(f'Applying {color} -> {f} ...')
                info = set_folder_icon(f, color)
                self.log(f'Done: {info}')
            except Exception as e:
                self.log(f'Error applying {f}: {e}')

    def remove_color(self):
        sels = list(self.listbox.curselection())
        if not sels:
            messagebox.showinfo('No folder', 'Select one or more folders to remove color from.')
            return
        folders = [self.folders[i] for i in sels]
        t = threading.Thread(target=self._remove_worker, args=(folders,), daemon=True)
        t.start()

    def _remove_worker(self, folders: list[str]):
        for f in folders:
            try:
                self.log(f'Removing color -> {f} ...')
                removed = remove_folder_icon(f)
                self.log(f'Removed: {removed}')
            except Exception as e:
                self.log(f'Error removing {f}: {e}')

    def self_test(self):
        t = threading.Thread(target=self._self_test_worker, daemon=True)
        t.start()

    def _self_test_worker(self):
        base = Path(__file__).parent / 'test_output_gui'
        base.mkdir(exist_ok=True)
        fld = base / 'test_gui_folder'
        try:
            info = set_folder_icon(str(fld), '#00ccff')
            self.log(f'Self-test created: {info}')
        except Exception as e:
            self.log(f'Self-test error: {e}')

    def log(self, msg: str):
        self.log_text.configure(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.configure(state='disabled')


def headless_test():
    m = load_colorize_module()
    base = Path(__file__).parent / 'test_output_gui'
    base.mkdir(exist_ok=True)
    fld = base / 'test_gui_folder'
    info = m.set_folder_icon(str(fld), '#00ccff')
    print('Headless GUI test created:', info)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='gui.py')
    parser.add_argument('--test', action='store_true', help='Run headless self-test and exit')
    parser.add_argument('--target', '-t', help='Target folder path to pre-add or operate on')
    parser.add_argument('--pick', action='store_true', help='With --target: open color chooser, apply the color and exit')
    args = parser.parse_args()
    if args.test:
        try:
            headless_test()
            sys.exit(0)
        except Exception as e:
            print('Headless GUI test failed:', e)
            sys.exit(2)

    # Quick-pick mode for context-menu usage: choose a color and apply to target folder, then exit
    if args.target and args.pick:
        if tk is None:
            print('Tkinter not available. Install Python with Tk support.')
            sys.exit(1)
        root = tk.Tk()
        root.withdraw()
        try:
            c = colorchooser.askcolor(color='#ffcc00', title='Pick a color for folder')
            if c and c[1]:
                color = c[1]
                info = set_folder_icon(args.target, color)
                print('Applied:', info)
                sys.exit(0)
            else:
                print('No color selected')
                sys.exit(2)
        finally:
            try:
                root.destroy()
            except Exception:
                pass

    if tk is None:
        print('Tkinter not available. Install Python with Tk support.')
        sys.exit(1)
    root = tk.Tk()
    app = App(root)
    if args.target:
        # pre-add and select the provided target folder in the GUI
        if args.target not in app.folders:
            app.folders.append(args.target)
            app.listbox.insert('end', args.target)
            idx = app.listbox.size() - 1
            if idx >= 0:
                app.listbox.selection_clear(0, 'end')
                app.listbox.selection_set(idx)
    root.mainloop()
