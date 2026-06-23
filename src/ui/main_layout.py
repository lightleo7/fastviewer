import asyncio
import os
import shlex
import flet as ft
from src.ui import add_to_history
from src.ui.search_page import SearchPage
from src.ui.history_page import HistoryPage
from src.ui.settings_page import SettingsPage


class MainLayout:

    def __init__(self, page: ft.Page):
        self.page = page

        self.search_component = SearchPage(page, self.play_in_mpv)
        self.history_component = HistoryPage(page, self.play_in_mpv)
        self.settings_component = SettingsPage(page)

        self.content_container = ft.Container(expand=True)
        self.nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.SEARCH_ROUNDED, selected_icon=ft.Icons.SEARCH, label="Поиск"),
                ft.NavigationRailDestination(icon=ft.Icons.HISTORY_ROUNDED, selected_icon=ft.Icons.HISTORY, label="История"),
                ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_ROUNDED, selected_icon=ft.Icons.SETTINGS, label="Настройки"),
            ],
            on_change=self.on_nav_change,
        )

    def build(self):
        self.content_container.content = self.search_component.build()
        self.page.add(
            ft.Row(
                controls=[self.nav_rail, ft.VerticalDivider(width=1), self.content_container],
                expand=True,
                spacing=0,
            )
        )

    def on_nav_change(self, e):
        index = self.nav_rail.selected_index
        if index == 0:
            self.content_container.content = self.search_component.build()
        elif index == 1:
            self.history_component.refresh_history()
            self.content_container.content = self.history_component.build()
        elif index == 2:
            self.content_container.content = self.settings_component.build()
        self.page.update()

    async def play_in_mpv(self, video: dict):
        """Асинхронно запускает MPV с кастомными флагами из конфигурации."""
        await add_to_history(self.page, video)

        info_snackbar = ft.SnackBar(
            content=ft.Text("Запуск плеера... Подождите, MPV скоро откроется", color=ft.Colors.WHITE),
            bgcolor=ft.Colors.BLUE_GREY_800,
            duration=3000,
        )
        self.page.overlay.append(info_snackbar)
        info_snackbar.open = True
        self.page.update()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, "../.."))
        local_mpv = os.path.join(project_root, "mpv.exe")
        cmd = local_mpv if os.path.exists(local_mpv) else "mpv"

        settings = self.page.session.store.get("settings") or {}
        raw_flags = settings.get("mpv_flags", "")
        
        flags_args = shlex.split(raw_flags)

        try:
            await asyncio.create_subprocess_exec(
                cmd, *flags_args, video["url"],
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
        except FileNotFoundError:
            error_snackbar = ft.SnackBar(
                content=ft.Text("Ошибка: плеер MPV не найден в системе!", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.RED_700,
                duration=5000,
            )
            self.page.overlay.append(error_snackbar)
            error_snackbar.open = True
            self.page.update()
