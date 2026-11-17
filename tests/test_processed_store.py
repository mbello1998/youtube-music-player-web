from igtoyt.processed_store import ProcessedStore


def test_load_missing_file_is_empty(tmp_path):
    store = ProcessedStore.load(tmp_path / "processed.json")
    assert not store.is_post_processed("abc123")


def test_mark_then_save_then_load_round_trips(tmp_path):
    path = tmp_path / "processed.json"
    store = ProcessedStore.load(path)
    store.mark("abc123", status="added", video_id="yt1")
    store.save(path)
    reloaded = ProcessedStore.load(path)
    assert reloaded.is_post_processed("abc123")
    assert reloaded.has_video("yt1")


def test_mark_overwrites_existing_entry(tmp_path):
    store = ProcessedStore.load(tmp_path / "processed.json")
    store.mark("abc123", status="not_identified", video_id=None)
    store.mark("abc123", status="added", video_id="yt1")
    assert store.has_video("yt1")
