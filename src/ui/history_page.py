import asyncio
import flet as ft
from src.ui import HISTORY_FILE
from src.ui.cards import build_video_card


class HistoryPage:

    def __init__(self, page: ft.Page, play_callback):
        self.page = page
        self.play_callback = play_callback
        self.list_view = ft.ListView(expand=True, spacing=10, padding=10)

    def build(self) -> ft.Container:
        self.refresh_history()
        clear_btn = ft.TextButton(
            "Очистить историю", icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=self.clear_history
        )
        header = ft.Row(
            controls=[ft.Text("История просмотров", size=20, weight=ft.FontWeight.BOLD, expand=True), clear_btn],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        return ft.Container(
            content=ft.Column(controls=[header, self.list_view], expand=True),
            padding=ft.Padding(left=20, top=20, right=20, bottom=20),
            expand=True,
        )

    def refresh_history(self):
        self.list_view.controls.clear()
        history = self.page.session.store.get("history") or []

        if not history:
            self.list_view.controls.append(
                ft.Row(
                    [ft.Text("История пуста. Здесь будут отображаться запущенные видео.", color=ft.Colors.GREY_500)],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
            return

        for item in history:
            card = build_video_card(item, self.play_callback)
            self.list_view.controls.append(card)

    def clear_history(self, e):
        self.page.session.store.set("history", [])
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("[]")
        self.refresh_history()
        self.page.update()
