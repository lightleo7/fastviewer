import asyncio
import flet as ft
from src.parsers import ALL_PARSERS
from src.ui.cards import build_video_card


class SearchPage:

    def __init__(self, page: ft.Page, play_callback):
        self.page = page
        self.play_callback = play_callback

        ELEMENT_HEIGHT = 48
        RADIUS = 12

        self.search_input = ft.TextField(
            hint_text="Введите поисковый запрос...",
            expand=True,
            height=ELEMENT_HEIGHT,
            border_radius=RADIUS,
            content_padding=ft.Padding(left=15, top=0, right=15, bottom=0),
            on_submit=self.on_search_click,
        )
        self.search_button = ft.ElevatedButton(
            "Найти",
            icon=ft.Icons.SEARCH,
            height=ELEMENT_HEIGHT,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIUS)),
            on_click=self.on_search_click,
        )
        self.loader = ft.ProgressRing(visible=False, width=40, height=40)
        self.results_list = ft.ListView(expand=True, spacing=10, padding=10)

    def build(self) -> ft.Container:
        search_row = ft.Row(
            controls=[self.search_input, self.search_button],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        return ft.Container(
            content=ft.Column(controls=[search_row, ft.Container(height=10), ft.Row([self.loader], alignment=ft.MainAxisAlignment.CENTER), self.results_list], expand=True),
            padding=ft.Padding(left=20, top=20, right=20, bottom=20),
            expand=True,
        )

    async def on_search_click(self, e):
        query = self.search_input.value
        if not query.strip():
            return

        active_tasks = []
        settings = self.page.session.store.get("settings") or {}
        parsers_config = settings.get("parsers", {})
        
        for name, parser in ALL_PARSERS.items():
            if parsers_config.get(name, True):
                active_tasks.append(parser.search(query))

        if not active_tasks:
            self.results_list.controls.clear()
            self.results_list.controls.append(ft.Row([ft.Text("Все парсеры выключены!", color=ft.Colors.RED_400)], alignment=ft.MainAxisAlignment.CENTER))
            self.page.update()
            return

        self.loader.visible = True
        self.results_list.controls.clear()
        self.search_button.disabled = True
        self.page.update()

        responses = await asyncio.gather(*active_tasks)
        all_videos = []
        for repo in responses:
            all_videos.extend(repo)

        self.loader.visible = False
        self.search_button.disabled = False

        if not all_videos:
            self.results_list.controls.append(ft.Row([ft.Text("Ничего не найдено.")], alignment=ft.MainAxisAlignment.CENTER))
        else:
            for video in all_videos:
                # Строим карточку из общего модуля
                card = build_video_card(video, self.play_callback)
                self.results_list.controls.append(card)
        self.page.update()
