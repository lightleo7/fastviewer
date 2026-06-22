import httpx
from src.parsers.base import BaseVideoParser


class RutubeParser(BaseVideoParser):

    @property
    def source_name(self) -> str:
        return "Rutube"

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://rutube.ru",
        }

    async def search(self, query: str) -> list[dict]:
        if not query.strip():
            return []

        formatted_query = query.strip().replace(" ", "+")
        url = f"https://rutube.ru/api/search/combined/video_playlist?query={formatted_query}&client=wdp&page=1&per_page=20"

        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True, timeout=12.0) as client:
            try:
                await client.get("https://rutube.ru")
                response = await client.get(url)
                if response.status_code != 200:
                    return []

                data = response.json()
                results = data.get("results", [])
                
                videos = []
                for item in results:
                    content_type = item.get("content_type", "video")
                    item_id = item.get("id")
                    
                    if not item_id:
                        continue
                    
                    if content_type == "playlist":
                        video_url = f"https://rutube.ru/plst/{item_id}/"
                    else:
                        video_url = item.get("video_url") or f"https://rutube.ru/video/{item_id}/"
                    
                    author_data = item.get("author") or {}
                    author_name = author_data.get("name", "Неизвестный автор")
                    img_url = item.get("thumbnail_url") or item.get("picture") or ""
                    
                    videos_count = item.get("videos_count") if content_type == "playlist" else None
                    
                    videos.append({
                        "id": item_id,
                        "title": item.get("title", "Без названия"),
                        "url": video_url,
                        "image": img_url,
                        "author": author_name,
                        "type": content_type,
                        "source": self.source_name,
                        "videos_count": videos_count
                    })
                
                return videos

            except Exception as e:
                print(f"[Rutube Search Error]: {e}")
                return []
