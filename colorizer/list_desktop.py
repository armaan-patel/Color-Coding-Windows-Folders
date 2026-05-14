from pathlib import Path
import json

def get_desktop_path():
    try:
        from win32com.shell import shell, shellcon
        p = shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)
        return Path(p)
    except Exception:
        # fallback
        return Path.home() / 'Desktop'

def main():
    desk = get_desktop_path()
    if not desk.exists():
        print(json.dumps({'error': 'Desktop not found', 'path': str(desk)}))
        return
    folders = [p.name for p in desk.iterdir() if p.is_dir()]
    print(json.dumps(sorted(folders, key=lambda x: x.lower())))

if __name__ == '__main__':
    main()
