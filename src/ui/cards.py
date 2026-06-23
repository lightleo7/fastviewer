import asyncio
import flet as ft


def build_video_card(video: dict, play_callback) -> ft.Card:
    """Генерирует универсальную горизонтальную карточку видео/плейлиста для поиска и истории."""
    is_playlist = video["type"] == "playlist"

    type_text = "ПЛЕЙЛИСТ" if is_playlist else "ВИДЕО"
    if is_playlist and video.get("videos_count") is not None:
        type_text += f" ({video['videos_count']} шт.)"

    type_badge = ft.Container(
        content=ft.Text(type_text, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.DEEP_PURPLE_700 if is_playlist else ft.Colors.RED_700,
        padding=ft.Padding(left=6, top=2, right=6, bottom=2),
        border_radius=4,
    )

    source_badge = ft.Container(
        content=ft.Text(video["source"].upper(), size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.BLUE_700,
        padding=ft.Padding(left=6, top=2, right=6, bottom=2),
        border_radius=4,
    )

    time_badge = None
    if "viewed_at" in video:
        time_badge = ft.Text(f"({video["viewed_at"]})", size=11, color=ft.Colors.GREY_500)

    row_badges = [source_badge, type_badge]
    if time_badge:
        row_badges.append(time_badge)
    row_badges.append(
        ft.Text(video["author"], size=12, color=ft.Colors.GREY_400, overflow=ft.TextOverflow.ELLIPSIS)
    )

    return ft.Card(
        content=ft.Container(
            padding=10,
            on_click=lambda e: asyncio.create_task(play_callback(video)),
            content=ft.Row(
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Image(
                        src=video["image"] or "https://placehold.co",
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
                            ft.Row(controls=row_badges, spacing=10),
                            ft.Text(
                                video["title"],
                                weight=ft.FontWeight.BOLD,
                                size=15,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_ARROW_ROUNDED,
                        icon_color=ft.Colors.RED_ACCENT,
                        icon_size=30,
                        on_click=lambda e: asyncio.create_task(play_callback(video)),
                    ),
                ],
            ),
        )
    )
