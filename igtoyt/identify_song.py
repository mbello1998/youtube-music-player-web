import asyncio
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

from igtoyt.instagram_saved import SavedPost


@dataclass
class SongMatch:
    query: str
    title: Optional[str]
    artist: Optional[str]
    method: Literal["metadata", "fingerprint", "caption_guess"]
    confidence: Literal["exact", "guess"]


def identify_from_metadata(post: SavedPost) -> Optional[SongMatch]:
    if not post.audio_title or not post.audio_artist:
        return None
    return SongMatch(
        query=f"{post.audio_title} {post.audio_artist}",
        title=post.audio_title,
        artist=post.audio_artist,
        method="metadata",
        confidence="exact",
    )


def identify_from_audio_fingerprint(video_path: Path, recognizer) -> Optional[SongMatch]:
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = Path(tmpdir) / "audio.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), "-vn", str(audio_path)],
            check=False,
            capture_output=True,
        )
        track = recognizer(audio_path)

    if not track:
        return None
    title = track.get("title")
    artist = track.get("artist")
    return SongMatch(
        query=f"{title} {artist}".strip(),
        title=title,
        artist=artist,
        method="fingerprint",
        confidence="exact",
    )


def identify_from_caption(post: SavedPost) -> Optional[SongMatch]:
    text = " ".join([post.caption or "", *post.hashtags]).strip()
    if not text:
        return None
    return SongMatch(query=text, title=None, artist=None, method="caption_guess", confidence="guess")


def identify_song(post: SavedPost, video_path: Optional[Path], recognizer) -> Optional[SongMatch]:
    match = identify_from_metadata(post)
    if match is not None:
        return match

    if video_path is not None:
        match = identify_from_audio_fingerprint(video_path, recognizer)
        if match is not None:
            return match

    return identify_from_caption(post)


def shazamio_recognize(audio_path: Path) -> Optional[dict]:
    import shazamio

    async def _recognize():
        shazam = shazamio.Shazam()
        try:
            return await shazam.recognize(str(audio_path))
        finally:
            await shazam.close()

    try:
        result = asyncio.run(_recognize())
    except Exception:
        return None
    track = result.get("track") if result else None
    if not track:
        return None
    return {"title": track.get("title"), "artist": track.get("subtitle")}
