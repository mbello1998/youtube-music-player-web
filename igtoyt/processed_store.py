import json
from pathlib import Path


class ProcessedStore:
    def __init__(self, entries: dict[str, dict] | None = None):
        self._entries = entries if entries is not None else {}

    @classmethod
    def load(cls, path: Path) -> "ProcessedStore":
        path = Path(path)
        if not path.exists():
            return cls()
        with path.open("r", encoding="utf-8") as f:
            return cls(json.load(f))

    def save(self, path: Path) -> None:
        path = Path(path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self._entries, f)

    def is_post_processed(self, shortcode: str) -> bool:
        return shortcode in self._entries

    def has_video(self, video_id: str) -> bool:
        return any(entry.get("video_id") == video_id for entry in self._entries.values())

    def mark(self, shortcode: str, status: str, video_id: str | None) -> None:
        self._entries[shortcode] = {"status": status, "video_id": video_id}
