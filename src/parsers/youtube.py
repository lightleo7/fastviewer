# not working<
import httpx
from src.parsers.base import BaseVideoParser


class YouTubeParser(BaseVideoParser):

    @property
    def source_name(self) -> str:
        return "YouTube"

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
        }

    async def search(self, query: str) -> list[dict]:
        if not query.strip():
            return []

        # Базовый endpoint десктопного поиска YouTube
        url = "https://youtube.com"
        
        # Имитируем официальный веб-интерфейс (WEB)
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20240501.01.00",
                    "hl": "ru",
                    "gl": "RU",
                    "utcOffsetMinutes": 180
                }
            },
            "query": query.strip()
        }

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=12.0) as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code != 200:
                    return []

                data = response.json()
                
                # Собираем абсолютно все рендереры, независимо от того, как глубоко их спрятал YouTube
                renderers = list(self._find_keys_elements(data, ["videoRenderer", "playlistRenderer"]))
                
                videos = []
                for key, item_data in renderers:
                    
                    # 1. ОБРАБОТКА ВИДЕО
                    if key == "videoRenderer":
                        video_id = item_data.get("videoId")
                        if not video_id:
                            continue
                            
                        thumbnails = item_data.get("thumbnail", {}).get("thumbnails", [])
                        img_url = thumbnails[-1]["url"] if thumbnails else ""
                        
                        title = self._parse_text_node(item_data.get("title"))
                        author_name = self._parse_text_node(item_data.get("shortBylineText"))

                        videos.append({
                            "id": video_id,
                            "title": title or "Без названия",
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "image": img_url,
                            "author": author_name or "Неизвестный автор",
                            "type": "video",
                            "source": self.source_name,
                            "videos_count": None
                        })

                    # 2. ОБРАБОТКА ПЛЕЙЛИСТОВ
                    elif key == "playlistRenderer":
                        playlist_id = item_data.get("playlistId")
                        if not playlist_id:
                            continue
                            
                        thumbnails = item_data.get("thumbnails", [{}]).get("thumbnails", [])
                        img_url = thumbnails[-1]["url"] if thumbnails else ""
                        
                        title = self._parse_text_node(item_data.get("title"))
                        author_name = self._parse_text_node(item_data.get("longBylineText"))
                        
                        # Извлекаем число видео из строки (например, "12 видео")
                        raw_count = item_data.get("videoCount", "0")
                        digits = "".join(filter(str.isdigit, str(raw_count)))
                        videos_count = int(digits) if digits else 0

                        videos.append({
                            "id": playlist_id,
                            "title": title or "Без названия",
                            "url": f"https://youtube.com{playlist_id}",
                            "image": img_url,
                            "author": author_name or "Неизвестный автор",
                            "type": "playlist",
                            "source": self.source_name,
                            "videos_count": videos_count
                        })

                return videos

            except Exception as e:
                print(f"[YouTube Search Error]: {e}")
                return []

    def _find_keys_elements(self, target_dict: dict | list, search_keys: list) -> list:
        """Рекурсивно ищет любые нужные ключи в древовидном JSON."""
        if isinstance(target_dict, dict):
            for k, v in target_dict.items():
                if k in search_keys:
                    yield k, v
                elif isinstance(v, (dict, list)):
                    yield from self._find_keys_elements(v, search_keys)
        elif isinstance(target_dict, list):
            for item in target_dict:
                if isinstance(item, (dict, list)):
                    yield from self._find_keys_elements(item, search_keys)

    def _parse_text_node(self, node: dict | None) -> str:
        """Универсально вытаскивает текст как из simpleText, так и из массивов runs."""
        if not node or not isinstance(node, dict):
            return ""
        if "simpleText" in node:
            return str(node["simpleText"])
        if "runs" in node and isinstance(node["runs"], list):
            return "".join([run.get("text", "") for run in node["runs"] if isinstance(run, dict)])
        return ""
