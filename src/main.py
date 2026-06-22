import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import flet as ft
from src.ui.router import AppRouter


def main(page: ft.Page):
    page.title = "Multi-Source Video FastViewer"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1050
    page.window_height = 850

    router = AppRouter(page)

    page.route = "/"
    
    router.on_route_change(None)


if __name__ == "__main__":
    ft.run(main)
