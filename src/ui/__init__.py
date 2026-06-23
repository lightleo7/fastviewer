import json
import os
from pathlib import Path
import flet as ft
from src.parsers import ALL_PARSERS

CONFIG_DIR = Path(os.getenv("APPDATA") or Path.home() / ".config") / "fastviewer"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

SETTINGS_FILE = CONFIG_DIR / "config.json"
HISTORY_FILE = CONFIG_DIR / "history.json"


async def init_storage(page: ft.Page):
    """Инициализирует настройки (включая флаги MPV) и историю из файлов JSON."""
    
    default_settings = {
        "parsers": {name: True for name in ALL_PARSERS.keys()},
        "mpv_flags": "--save-position-on-quit --ytdl-format=bestvideo[height<=1080]+bestaudio/best"
    }
    
    # 1. Загрузка или создание config.json
    if not SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4, ensure_ascii=False)
        page.session.store.set("settings", default_settings)
    else:
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved_settings = json.load(f)
            
            if "parsers" not in saved_settings:
                saved_settings = default_settings
            else:
                for name in default_settings["parsers"]:
                    if name not in saved_settings["parsers"]:
                        saved_settings["parsers"][name] = True
                if "mpv_flags" not in saved_settings:
                    saved_settings["mpv_flags"] = default_settings["mpv_flags"]
                    
            page.session.store.set("settings", saved_settings)
        except Exception:
            page.session.store.set("settings", default_settings)

    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        page.session.store.set("history", [])
    else:
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                saved_history = json.load(f)
            page.session.store.set("history", saved_history)
        except Exception:
            page.session.store.set("history", [])


async def add_to_history(page: ft.Page, video_data: dict):
    """Добавляет ПОЛНЫЙ объект видео в историю просмотров со штампом времени."""
    import datetime
    
    history = page.session.store.get("history") or []
    
    entry = video_data.copy()
    entry["viewed_at"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    
    history = [item for item in history if item["url"] != entry["url"]]
    history.insert(0, entry)
    history = history[:50]
    
    page.session.store.set("history", history)
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)
