from dataclasses import dataclass
from typing import Optional

import yt_dlp


@dataclass
class VideoResult:
    video_id: str
    title: str
    url: str


def real_ytdlp_extractor(query: str) -> dict:
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        return ydl.extract_info(f"ytsearch1:{query}", download=False)


def search_youtube(query: str, ytdlp_extractor=real_ytdlp_extractor) -> Optional[VideoResult]:
    try:
        info = ytdlp_extractor(query)
    except Exception:
        return None

    entries = info.get("entries") or []
    if not entries:
        return None

    entry = entries[0]
    return VideoResult(video_id=entry["id"], title=entry["title"], url=entry["webpage_url"])
