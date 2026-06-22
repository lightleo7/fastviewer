from src.parsers.rutube import RutubeParser
from src.parsers.vk import VkVideoParser
from src.parsers.youtube import YouTubeParser
import asyncio

ALL_PARSERS = {
    "Rutube": RutubeParser(),
    # "VK Видео": VkVideoParser(),
    # "YouTube": YouTubeParser(),
}

# if __name__ == "__main__:":
# async def main():
#     active_tasks = []
#     for name, parser in ALL_PARSERS.items():
        
#         active_tasks.append(parser.search("marmok"))

#     responses = await asyncio.gather(*active_tasks)

#     all_videos = []
#     for repo in responses:
#         all_videos.extend(repo)
#     print(all_videos)

# asyncio.run(main())