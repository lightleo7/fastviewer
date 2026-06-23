# not working<
import re
import html
import httpx
from src.parsers.base import BaseVideoParser


class VkVideoParser(BaseVideoParser):

    @property
    def source_name(self) -> str:
        return "VK Видео"

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Mobile Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def search(self, query: str) -> list[dict]:
        if not query.strip():
            return []

        formatted_query = query.strip().replace(" ", "+")
        url = f"https://vk.com/?q={formatted_query}"

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=12.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return []

                html_content = response.text

                # Регулярное выражение находит все блоки видео на мобильной странице
                # Каждый блок содержит data-id (owner_id + video_id) и вложенные теги с данными
                video_blocks = re.findall(r"<div[^>]*class=\"[^\"]*v_item[^\"]*\"[^>]*>.*?<\/div>\s*<\/div>", html_content, re.DOTALL)
                
                # Если мобильная верстка слегка отличается, используем более точечный поиск по ссылкам
                if not video_blocks:
                    video_blocks = re.findall(r"<a[^>]*href=\"\/video-[^\"]*\"[^>]*>.*?<\/a>", html_content, re.DOTALL)

                videos = []
                
                # Ищем данные через универсальный сборщик по регулярным выражениям прямо из HTML-атрибутов
                # VK всегда зашивает метаданные роликов в data-атрибуты карточек
                items_data = re.findall(r"data-id=\"(-?\d+_\d+)\"[^>]*data-title=\"([^\"]*)\"[^>]*data-thumb=\"([^\"]*)\"[^>]*data-author=\"([^\"]*)\"", html_content)

                for item in items_data:
                    full_id, raw_title, raw_thumb, raw_author = item
                    
                    # Декодируем HTML-сущности (например, &quot; или &#39;) в нормальный текст
                    title = html.unescape(raw_title)
                    author = html.unescape(raw_author)
                    img_url = html.unescape(raw_thumb)

                    videos.append({
                        "id": full_id,
                        "title": title or "Без названия",
                        "url": f"https://vkvideo.ru{full_id}",
                        "image": img_url,
                        "author": author or "Неизвестный автор",
                        "type": "video",
                        "source": self.source_name,
                        "videos_count": None
                    })

                # Резервный вариант: если data-атрибуты скрыты, парсим стандартные теги карточки мобильной выдачи
                if not videos:
                    items_blocks = re.findall(r"href=\"\/video(-?\d+_\d+)\".*?class=\"v_title\">([^<]*).*?style=\"background-image:url\('([^\']*)'\)", html_content, re.DOTALL)
                    for block in items_blocks:
                        full_id, raw_title, img_url = block
                        videos.append({
                            "id": full_id,
                            "title": raw_title.strip() or "Без названия",
                            "url": f"https://vkvideo.ru{full_id}",
                            "image": img_url,
                            "author": "Канал VK Видео",  # В базовой мобильной разметке имя автора выносим дефолтом
                            "type": "video",
                            "source": self.source_name,
                            "videos_count": None
                        })

                return videos

            except Exception as e:
                print(f"[VK Mobile Web Search Error]: {e}")
                return []
