from src.parsers.rutube import RutubeParser
from src.parsers.vk import VkVideoParser
from src.parsers.youtube import YouTubeParser
import asyncio

ALL_PARSERS = {
    "Rutube": RutubeParser(),
    # "VK Видео": VkVideoParser(),
    "YouTube": YouTubeParser(),
}