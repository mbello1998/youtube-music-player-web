from igtoyt.youtube_search import VideoResult, search_youtube


def test_search_returns_first_entry():
    fake_info = {"entries": [{"id": "vid1", "title": "Song - Artist", "webpage_url": "https://youtu.be/vid1"}]}
    result = search_youtube("Song Artist", ytdlp_extractor=lambda q: fake_info)
    assert result == VideoResult("vid1", "Song - Artist", "https://youtu.be/vid1")


def test_search_returns_none_on_empty_entries():
    assert search_youtube("nothing", ytdlp_extractor=lambda q: {"entries": []}) is None


def test_search_returns_none_on_extractor_error():
    def boom(q):
        raise RuntimeError("network down")

    assert search_youtube("x", ytdlp_extractor=boom) is None
