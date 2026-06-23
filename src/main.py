import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flet as ft
from src.ui import init_storage
from src.ui.main_layout import MainLayout


async def main(page: ft.Page):
    page.title = "Multi-Source Video FastViewer"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 1300
    page.window.height = 800

    await init_storage(page)

    layout = MainLayout(page)
    layout.build()


if __name__ == "__main__":
    ft.run(main)
