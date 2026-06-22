import flet as ft
from src.ui import APP_SETTINGS


class SettingsPage:

    def __init__(self, page: ft.Page):
        self.page = page
        self.checkboxes = {}

    def build(self) -> ft.View:
        """Генерирует отдельный View (экран) настроек."""
        self.checkboxes.clear()

        for name, is_enabled in APP_SETTINGS.items():
            self.checkboxes[name] = ft.Checkbox(
                label=name, value=is_enabled, on_change=self.on_checkbox_change
            )

        parsers_list = ft.Column(
            controls=[
                ft.Text(
                    "Включение / Выключение поисковых модулей:",
                    size=16,
                    color=ft.Colors.GREY_400,
                ),
                ft.Container(height=10),
                *self.checkboxes.values(),
            ],
            spacing=10,
        )

        return ft.View(
            route="/settings",
            controls=[
                ft.AppBar(
                    title=ft.Text("Настройки источников"),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                    leading=ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        tooltip="Назад к поиску",
                        on_click=lambda _: [setattr(self.page, 'route', '/'), self.page.go(self.page.route)],
                    ),
                ),
                ft.Container(
                    content=parsers_list, 
                    padding=ft.Padding(left=20, top=20, right=20, bottom=20), 
                    expand=True
                ),
            ],
        )

    def on_checkbox_change(self, e):
        """Сохраняет состояние чекбоксов в глобальный словарь при клике."""
        for name, cb in self.checkboxes.items():
            APP_SETTINGS[name] = cb.value
