# not working< | in progress
import json
import re
import httpx
from src.parsers.base import BaseVideoParser


class VkVideoParser(BaseVideoParser):

    @property
    def source_name(self) -> str:
        return "VK Видео"

    def __init__(self):
        # Обычные десктопные заголовки для загрузки страницы
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def search(self, query: str) -> list[dict]:
        if not query.strip():
            return []

        # Форматируем поисковый запрос для URL
        formatted_query = query.strip().replace(" ", "+")
        # Переходим на страницу веб-поиска платформы
        url = f"https://vkvideo.ru/?q={formatted_query}"

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=15.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return []

                html_content = response.text

                # Находим на странице JS-объект, содержащий JSON-выдачу каталога
                # ВК всегда отдает начальные данные в объекте вида extendConfig(...) или аналогичном стейте
                match = re.search(r"\"items\"\s*:\s*(\[.*?\])\s*,\s*\"profiles\"", html_content, re.DOTALL)
                
                # Если регулярка выше не зацепилась из-за минификации, используем более широкий поиск блоков данных
                if not match:
                    match = re.search(r"catalogGrid.*?\"items\"\s*:\s*(\[.*?\])\s*[,}]", html_content, re.DOTALL)

                if not match:
                    # Попытка вытащить данные через общий JSON-контейнер страницы
                    state_match = re.search(r"window\.extendConfig\s*=\s*(\{.*?\});", html_content, re.DOTALL)
                    if state_match:
                        try:
                            state_data = json.loads(state_match.group(1))
                            # Ищем рекурсивно блоки с результатами
                            return self._parse_from_dict(state_data)
                        except Exception:
                            pass
                    return []

                # Извлекаем и парсим чистый JSON массив элементов
                try:
                    items_json = match.group(1)
                    # Корректируем возможные синтаксические особенности JS-объектов в строке
                    items = json.loads(items_json)
                except (ValueError, IndexError):
                    return []

                # Извлекаем карты авторов со страницы для склеивания имен
                authors_map = {}
                profiles_match = re.search(r"\"profiles\"\s*:\s*(\[.*?\])\s*,\s*\"groups\"", html_content, re.DOTALL)
                groups_match = re.search(r"\"groups\"\s*:\s*(\[.*?\])\s*[,}]", html_content, re.DOTALL)

                if profiles_match:
                    try:
                        for p in json.loads(profiles_match.group(1)):
                            p_id = p.get("id")
                            authors_map[p_id] = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                            authors_map[abs(p_id)] = authors_map[p_id]
                    except Exception:
                        pass

                if groups_match:
                    try:
                        for g in json.loads(groups_match.group(1)):
                            g_id = g.get("id")
                            authors_map[g_id] = g.get("name", "Группа")
                            authors_map[-abs(g_id)] = g.get("name", "Группа")
                    except Exception:
                        pass

                return self._build_video_list(items, authors_map)

            except Exception as e:
                print(f"[VK Video Search Exception]: {e}")
                return []

    def _build_video_list(self, items: list, authors_map: dict) -> list[dict]:
        """Форматирует плоский список элементов под ваш BaseVideoParser."""
        videos = []
        for item in items:
            video_id = item.get("id")
            owner_id = item.get("owner_id") or item.get("ownerId")
            if not video_id or owner_id is None:
                continue

            author_name = authors_map.get(owner_id, "Неизвестный автор")
            
            # Находим лучшее превью
            img_url = ""
            image_keys = ["photo_max", "photo_1280", "photo_800", "photo_640", "photo_320", "image"]
            for key in image_keys:
                if key in item:
                    img_url = item[key]
                    break
            
            if not img_url and "first_frame" in item:
                img_url = item["first_frame"]

            videos.append({
                "id": f"{owner_id}_{video_id}",
                "title": item.get("title", "Без названия"),
                "url": f"https://vkvideo.ru{owner_id}_{video_id}",
                "image": img_url,
                "author": author_name,
                "type": "video",
                "source": self.source_name,
                "videos_count": None
            })
        return videos

    def _parse_from_dict(self, data: dict) -> list[dict]:
        """Резервный рекурсивный поиск элементов внутри дерева конфигурации страницы."""
        # Быстрый поиск ключа items во вложенных словарях
        if isinstance(data, dict):
            if "items" in data and isinstance(data["items"], list):
                return self._build_video_list(data["items"], {})
            for v in data.values():
                res = self._parse_from_dict(v)
                if res:
                    return res
        elif isinstance(data, list):
            for item in data:
                res = self._parse_from_dict(item)
                if res:
                    return res
        return []
