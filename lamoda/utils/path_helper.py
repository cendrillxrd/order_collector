from pathlib import Path


def get_desktop_path() -> str:
    desktop_str = str(Path.home() / "Desktop")
    return desktop_str
