from igtoyt.instagram_saved import iter_saved_posts


class FakePost:
    """Mimics the subset of instaloader.Post this module reads.

    Real Post objects expose `_full_metadata` (a dict merging the raw
    GraphQL node with any lazily-fetched full metadata). When a reel uses
    an Instagram-library audio track, that dict carries a
    `clips_music_attribution_info` entry with `song_name`/`artist_name`.
    """

    def __init__(self, shortcode, caption, hashtags, is_video, music=None):
        self.shortcode = shortcode
        self.caption = caption
        self.caption_hashtags = hashtags
        self.is_video = is_video
        self._full_metadata = {"clips_music_attribution_info": music} if music else {}


def test_photo_post_is_skipped_not_downloaded(tmp_path):
    post = FakePost("abc", "a caption", ["tag1"], is_video=False)
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].is_video is False
    assert results[0].video_path is None


def test_video_post_with_music_attribution(tmp_path):
    post = FakePost("def", "caption", [], is_video=True, music={"song_name": "Song", "artist_name": "Artist"})
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].audio_title == "Song"
    assert results[0].audio_artist == "Artist"


def test_video_post_without_music_attribution_has_none_fields(tmp_path):
    post = FakePost("ghi", "caption", [], is_video=True, music=None)
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].audio_title is None
    assert results[0].audio_artist is None
