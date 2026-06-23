import flet as ft
import json
from src.ui import SETTINGS_FILE


class SettingsPage:

    def __init__(self, page: ft.Page):
        self.page = page
        self.checkboxes = {}
        
        # Текстовое поле для аргументов MPV
        self.flags_input = ft.TextField(
            label="Аргументы командной строки MPV (флаги)",
            hint_text="Например: --save-position-on-quit --volume=80",
            multiline=True,
            min_lines=2,
            max_lines=4,
            on_change=self.on_flags_change
        )

    def build(self) -> ft.Container:
        self.checkboxes.clear()
        current_settings = self.page.session.store.get("settings") or {}
        parsers_config = current_settings.get("parsers", {})
        
        # Устанавливаем текущее значение флагов в поле ввода
        self.flags_input.value = current_settings.get("mpv_flags", "")

        for name, is_enabled in parsers_config.items():
            self.checkboxes[name] = ft.Checkbox(
                label=name, value=is_enabled, on_change=self.on_checkbox_change
            )

        parsers_list = ft.Column(
            controls=[
                ft.Text("Настройки источников", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                ft.Text("Выберите, на каких площадках будет производиться поиск:", size=14, color=ft.Colors.GREY_400),
                *self.checkboxes.values(),
                ft.Container(height=15),
                ft.Text("Конфигурация плеера MPV:", size=14, color=ft.Colors.GREY_400),
                ft.Container(height=5),
                self.flags_input,
                ft.Container(height=5),
                ft.Text(
                    "Подсказка: флаг '--save-position-on-quit' сохраняет время. "
                    "Для ограничения качества до 720p используйте: '--ytdl-format=bestvideo[height<=720]+bestaudio/best'", 
                    size=11, color=ft.Colors.GREY_500
                )
            ],
            spacing=5,
        )

        return ft.Container(
            content=parsers_list,
            padding=ft.Padding(left=20, top=20, right=20, bottom=20),
            expand=True,
        )

    async def save_to_disk(self, updated_settings):
        """Вспомогательный метод перезаписи физического файла настроек."""
        self.page.session.store.set("settings", updated_settings)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_settings, f, indent=4, ensure_ascii=False)

    async def on_checkbox_change(self, e):
        """Обрабатывает изменение чекбоксов площадок."""
        current_settings = self.page.session.store.get("settings") or {}
        
        updated_parsers = {}
        for name, cb in self.checkboxes.items():
            updated_parsers[name] = cb.value
            
        current_settings["parsers"] = updated_parsers
        await self.save_to_disk(current_settings)

    async def on_flags_change(self, e):
        """Обрабатывает ввод флагов MPV на лету."""
        current_settings = self.page.session.store.get("settings") or {}
        current_settings["mpv_flags"] = self.flags_input.value
        await self.save_to_disk(current_settings)
