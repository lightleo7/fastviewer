import json
import httpx
from src.parsers.base import BaseVideoParser


class YouTubeParser(BaseVideoParser):

    @property
    def source_name(self) -> str:
        return "YouTube"

    def __init__(self):
        # Имитируем AJAX-клиент браузера со специальными заголовками
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "X-YouTube-Client-Name": "1",    # Сообщает серверу, что мы WEB-интерфейс
            "X-YouTube-Client-Version": "2.20240501.01.00",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    async def search(self, query: str) -> list[dict]:
        if not query.strip():
            return []

        formatted_query = query.strip().replace(" ", "+")
        
        url = f"https://youtube.com/results?search_query={formatted_query}&pbj=1"

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=12.0) as client:
            try:
                response = await client.get(url)
                if response.status_code != 200:
                    return []

                text_content = response.content.decode("utf-8", errors="replace")
                
                raw_data = json.loads(text_content)
                
                data = {}
                if isinstance(raw_data, list):
                    for part in raw_data:
                        if "response" in part:
                            data = part["response"]
                            break
                elif isinstance(raw_data, dict):
                    data = raw_data.get("response", raw_data)

                renderers = list(self._extract_renderers(data, ["videoRenderer", "playlistRenderer"]))
                
                videos = []
                for key, item in renderers:
                    if key == "videoRenderer":
                        video_id = item.get("videoId")
                        if not video_id:
                            continue
                            
                        thumbnails = item.get("thumbnail", {}).get("thumbnails", [])
                        img_url = thumbnails[-1]["url"] if thumbnails else ""
                        
                        title = self._get_text(item.get("title"))
                        author = self._get_text(item.get("shortBylineText"))

                        videos.append({
                            "id": video_id,
                            "title": title or "Без названия",
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "image": img_url,
                            "author": author or "Неизвестный автор",
                            "type": "video",
                            "source": self.source_name,
                            "videos_count": None
                        })

                    elif key == "playlistRenderer":
                        playlist_id = item.get("playlistId")
                        if not playlist_id:
                            continue
                            
                        thumbnails = item.get("thumbnails", [{}]).get("thumbnails", [])
                        img_url = thumbnails[-1]["url"] if thumbnails else ""
                        
                        title = self._get_text(item.get("title"))
                        author = self._get_text(item.get("longBylineText"))
                        
                        raw_count = item.get("videoCount", "0")
                        digits = "".join(filter(str.isdigit, str(raw_count)))
                        videos_count = int(digits) if digits else 0

                        videos.append({
                            "id": playlist_id,
                            "title": title or "Без названия",
                            "url": f"https://youtube.com{playlist_id}",
                            "image": img_url,
                            "author": author or "Неизвестный автор",
                            "type": "playlist",
                            "source": self.source_name,
                            "videos_count": videos_count
                        })

                return videos

            except Exception as e:
                print(f"[YouTube Native Parser Error]: {e}")
                return []

    def _extract_renderers(self, data: dict | list, keys: list) -> list:
        """Рекурсивно сканирует дерево любой глубины, вытягивая видео и плейлисты."""
        if isinstance(data, dict):
            for k, v in data.items():
                if k in keys:
                    yield k, v
                elif isinstance(v, (dict, list)):
                    yield from self._extract_renderers(v, keys)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    yield from self._extract_renderers(item, keys)

    def _get_text(self, node: dict | None) -> str:
        """Универсальный безопасный разбор текстовых полей YouTube."""
        if not node or not isinstance(node, dict):
            return ""
        if "simpleText" in node:
            return str(node["simpleText"])
        if "runs" in node and isinstance(node["runs"], list):
            return "".join([run.get("text", "") for run in node["runs"] if isinstance(run, dict)])
        return ""
