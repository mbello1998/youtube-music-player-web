from igtoyt.identify_song import (
    identify_from_audio_fingerprint,
    identify_from_caption,
    identify_from_metadata,
    identify_song,
)
from igtoyt.instagram_saved import SavedPost


def test_metadata_match_when_both_fields_present():
    post = SavedPost("a", "", [], True, None, audio_title="Song", audio_artist="Artist")
    match = identify_from_metadata(post)
    assert match.confidence == "exact" and match.method == "metadata"


def test_metadata_none_when_either_field_missing():
    post = SavedPost("a", "", [], True, None, audio_title="Song", audio_artist=None)
    assert identify_from_metadata(post) is None


def test_fingerprint_match_when_recognizer_finds_track(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    match = identify_from_audio_fingerprint(video, recognizer=lambda p: {"title": "Song", "artist": "Artist"})
    assert match.confidence == "exact" and match.method == "fingerprint"


def test_fingerprint_none_when_recognizer_finds_nothing(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    assert identify_from_audio_fingerprint(video, recognizer=lambda p: None) is None


def test_caption_guess_built_from_caption_and_hashtags():
    post = SavedPost("a", "ótima vibe", ["musica", "throwback"], True, None, None, None)
    match = identify_from_caption(post)
    assert match.confidence == "guess" and match.method == "caption_guess"


def test_caption_none_when_caption_and_hashtags_empty():
    post = SavedPost("a", "", [], True, None, None, None)
    assert identify_from_caption(post) is None


def test_cascade_stops_at_metadata():
    post = SavedPost("a", "caption", ["tag"], True, None, "Song", "Artist")
    calls = []
    identify_song(post, video_path=None, recognizer=lambda p: calls.append("fp"))
    assert "fp" not in calls


def test_cascade_falls_through_to_caption_when_others_absent():
    post = SavedPost("a", "caption", [], True, None, None, None)
    match = identify_song(post, video_path=None, recognizer=lambda p: None)
    assert match.method == "caption_guess"


def test_cascade_returns_none_when_everything_absent():
    post = SavedPost("a", "", [], True, None, None, None)
    assert identify_song(post, video_path=None, recognizer=lambda p: None) is None
