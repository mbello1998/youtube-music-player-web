from pathlib import Path

from igtoyt.identify_song import SongMatch
from igtoyt.instagram_saved import SavedPost
from igtoyt.main import run_pipeline
from igtoyt.processed_store import ProcessedStore
from igtoyt.youtube_search import VideoResult


def make_post(shortcode, is_video=True):
    return SavedPost(shortcode, "", [], is_video, None, None, None)


def test_already_processed_post_is_skipped(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    store.mark("done1", status="added", video_id="vidX")
    calls = {"identify": 0}

    def identify(post, path):
        calls["identify"] += 1
        return None

    run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=Path("."),
        saved_posts=[make_post("done1")],
        identify=identify,
        search=lambda q: None,
        add_to_playlist=lambda *a: True,
    )
    assert calls["identify"] == 0


def test_photo_post_recorded_as_skipped(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    report = run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("photo1", is_video=False)],
        identify=lambda post, path: None,
        search=lambda q: None,
        add_to_playlist=lambda *a: True,
    )
    assert report.skipped_photos == ["photo1"]


def test_unidentified_post_recorded(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    report = run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("v1")],
        identify=lambda post, path: None,
        search=lambda q: None,
        add_to_playlist=lambda *a: True,
    )
    assert report.not_identified == ["v1"]


def test_identified_but_not_found_on_youtube(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    match = SongMatch(query="x", title="t", artist="a", method="metadata", confidence="exact")
    report = run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("v2")],
        identify=lambda post, path: match,
        search=lambda q: None,
        add_to_playlist=lambda *a: True,
    )
    assert report.not_found_on_youtube == ["v2"]


def test_exact_match_added_guess_match_guessed(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    video = VideoResult("vid1", "t", "u")
    exact = SongMatch(query="x", title="t", artist="a", method="metadata", confidence="exact")
    guess = SongMatch(query="x", title=None, artist=None, method="caption_guess", confidence="guess")
    report = run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("v3")],
        identify=lambda post, path: exact,
        search=lambda q: video,
        add_to_playlist=lambda *a: True,
    )
    assert report.added == ["v3"]
    report2 = run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("v4")],
        identify=lambda post, path: guess,
        search=lambda q: video,
        add_to_playlist=lambda *a: True,
    )
    assert report2.guessed == ["v4"]


def test_rerun_with_everything_processed_touches_nothing(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    store.mark("v5", status="added", video_id="vid1")
    calls = {"n": 0}

    def identify(post, path):
        calls["n"] += 1
        return None

    run_pipeline(
        store,
        youtube=None,
        playlist_id="p",
        download_dir=tmp_path,
        saved_posts=[make_post("v5")],
        identify=identify,
        search=lambda q: None,
        add_to_playlist=lambda *a: True,
    )
    assert calls["n"] == 0
