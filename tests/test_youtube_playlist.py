from igtoyt.processed_store import ProcessedStore
from igtoyt.youtube_playlist import add_video_to_playlist, ensure_playlist


class FakeYouTube:
    def __init__(self, existing_playlists=(), insert_result="new-id"):
        self._existing = existing_playlists
        self._insert_result = insert_result
        self.insert_called = False

    def playlists(self):
        return self

    def playlistItems(self):
        return self

    def list(self, **kw):
        return self

    def insert(self, **kw):
        self.insert_called = True
        return self

    def execute(self):
        if self.insert_called:
            return {"id": self._insert_result}
        return {"items": [{"id": pid, "snippet": {"title": t}} for pid, t in self._existing]}


def test_ensure_playlist_returns_existing_match():
    yt = FakeYouTube(existing_playlists=[("p1", "Músicas do Instagram")])
    assert ensure_playlist(yt, "Músicas do Instagram") == "p1"
    assert yt.insert_called is False


def test_ensure_playlist_creates_when_missing():
    yt = FakeYouTube(existing_playlists=[])
    assert ensure_playlist(yt, "Músicas do Instagram") == "new-id"
    assert yt.insert_called is True


def test_add_video_skips_duplicate(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    store.mark("shortcode1", status="added", video_id="vid1")
    yt = FakeYouTube()
    assert add_video_to_playlist(yt, "pid", "vid1", store) is False
    assert yt.insert_called is False


def test_add_video_inserts_new(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    yt = FakeYouTube()
    assert add_video_to_playlist(yt, "pid", "vid1", store) is True
    assert yt.insert_called is True
