import flet as ft
from src.ui.search_page import SearchPage
from src.ui.settings_page import SettingsPage


class AppRouter:

    def __init__(self, page: ft.Page):
        self.page = page

        self.search_page = SearchPage(page)
        self.settings_page = SettingsPage(page)

        self.page.on_route_change = self.on_route_change

    def on_route_change(self, e: ft.RouteChangeEvent):
        """Очищает стек экранов и монтирует страницу в соответствии с текущим роутом."""
        self.page.views.clear()

        if self.page.route == "/settings":
            self.page.views.append(self.settings_page.build())
        else:
            self.page.views.append(self.search_page.build())

        self.page.update()
