import os
import flet as ft
from src.parsers import ALL_PARSERS
from src.ui import APP_SETTINGS
import asyncio

class SearchPage:

    def __init__(self, page: ft.Page):
        self.page = page

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
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS),
            ),
            on_click=self.on_search_click,
        )

        self.settings_button = ft.ElevatedButton(
            content=ft.Icon(ft.Icons.SETTINGS),
            height=ELEMENT_HEIGHT,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS),
                padding=ft.Padding(left=15, top=0, right=15, bottom=0),
            ),
            tooltip="Открыть настройки",
            on_click=lambda _: [setattr(self.page, 'route', '/settings'), self.page.go(self.page.route)],
        )

        self.loader = ft.ProgressRing(visible=False, width=40, height=40)
        self.results_list = ft.ListView(expand=True, spacing=0, padding=10)

    def build(self) -> ft.View:
        """Генерирует View (экран) поиска видео."""
        
        control_row = ft.Row(
            controls=[
                self.search_input, 
                self.search_button, 
                self.settings_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        loader_container = ft.Row(
            controls=[self.loader], alignment=ft.MainAxisAlignment.CENTER
        )

        return ft.View(
            route="/",
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            control_row,
                            ft.Container(height=10),
                            loader_container,
                            self.results_list,
                        ],
                        expand=True,
                    ),
                    padding=ft.Padding(left=20, top=20, right=20, bottom=20),
                    expand=True,
                ),
            ],
        )

    async def play_in_mpv(self, url: str):
        """Асинхронно запускает плеер MPV."""
        info_snackbar = ft.SnackBar(
            content=ft.Text(
                "Запуск плеера... Подождите, MPV скоро откроется",
                color=ft.Colors.WHITE,
            ),
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

        try:
            await asyncio.create_subprocess_exec(
                cmd,
                url,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
        except FileNotFoundError:
            error_snackbar = ft.SnackBar(
                content=ft.Text(
                    "Ошибка: плеер MPV не найден в системе!",
                    color=ft.Colors.WHITE,
                ),
                bgcolor=ft.Colors.RED_700,
                duration=5000,
            )
            self.page.overlay.append(error_snackbar)
            error_snackbar.open = True
            self.page.update()

    async def on_search_click(self, e):
        """Обработчик поиска с учетом фильтрации из глобальных настроек."""
        query = self.search_input.value
        if not query.strip():
            return

        active_tasks = []
        for name, parser in ALL_PARSERS.items():
            if APP_SETTINGS.get(name, True):
                active_tasks.append(parser.search(query))

        if not active_tasks:
            self.results_list.controls.clear()
            self.results_list.controls.append(
                ft.Row(
                    [
                        ft.Text(
                            "Все парсеры выключены! Нажмите на ⚙️ рядом с поиском и включите хотя бы один.",
                            color=ft.Colors.RED_400,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
            self.page.update()
            return

        self.loader.visible = True
        self.results_list.controls.clear()
        self.search_button.disabled = True
        self.settings_button.disabled = True
        self.page.update()

        responses = await asyncio.gather(*active_tasks)

        all_videos = []
        for repo in responses:
            all_videos.extend(repo)

        self.loader.visible = False
        self.search_button.disabled = False
        self.settings_button.disabled = False

        if not all_videos:
            self.results_list.controls.append(
                ft.Row(
                    [ft.Text("Ничего не найдено.")],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
        else:
            for video in all_videos:
                is_playlist = video["type"] == "playlist"

                type_text = "ПЛЕЙЛИСТ" if is_playlist else "ВИДЕО"
                if is_playlist and video.get("videos_count") is not None:
                    type_text += f" ({video['videos_count']} видео)"

                type_badge = ft.Container(
                    content=ft.Text(
                        type_text,
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=(
                        ft.Colors.DEEP_PURPLE_700
                        if is_playlist
                        else ft.Colors.RED_700
                    ),
                    padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                    border_radius=4,
                )

                source_badge = ft.Container(
                    content=ft.Text(
                        video["source"].upper(),
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.BLUE_700,
                    padding=ft.Padding(left=6, top=2, right=6, bottom=2),
                    border_radius=4,
                )

                card = ft.Card(
                    content=ft.Container(
                        padding=10,
                        on_click=lambda e, u=video["url"]: asyncio.create_task(
                            self.play_in_mpv(u)
                        ),
                        content=ft.Row(
                            spacing=15,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                ft.Image(
                                    src=(
                                        video["image"]
                                        or "https://placehold.co"
                                    ),
                                    fit=ft.BoxFit.COVER,
                                    width=180,
                                    height=100,
                                    border_radius=6,
                                ),
                                ft.VerticalDivider(visible=False),
                                ft.Column(
                                    expand=True,
                                    spacing=5,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                source_badge,
                                                type_badge,
                                                ft.Text(
                                                    video["author"],
                                                    size=12,
                                                    color=ft.Colors.GREY_400,
                                                    overflow=(
                                                        ft.TextOverflow.ELLIPSIS
                                                    ),
                                                ),
                                            ],
                                            spacing=10,
                                        ),
                                        ft.Text(
                                            video["title"],
                                            weight=ft.FontWeight.BOLD,
                                            size=15,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                ),
                                ft.IconButton(icon=ft.Icons.PLAY_ARROW_ROUNDED,
                                              icon_color=ft.Colors.BLUE_ACCENT,
                                              icon_size=30,
                                              on_click=lambda e, u=video["url"]: (asyncio.create_task(self.play_in_mpv(u))
                                            ),
                                            ),
                                    ],
                                ),
                            ))
                self.results_list.controls.append(card)
                self.page.update()