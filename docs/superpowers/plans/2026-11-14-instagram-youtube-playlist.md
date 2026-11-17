# Instagram → YouTube Playlist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Python tool that pulls the user's saved Instagram posts/reels, identifies the song in each (metadata → audio fingerprint → caption-text guess), finds the best YouTube match for each, and adds it to a YouTube playlist — resumable across runs with no duplicates.

**Architecture:** A chain of small, independently-testable modules under `igtoyt/` (Instagram auth → saved-post listing → song identification → YouTube search → YouTube auth → playlist writes), each exposing pure, dependency-injected functions so tests never touch the real network, wired together by `igtoyt/main.py`.

**Tech Stack:** Python 3.15 (already installed), `yt-dlp` and `ffmpeg` (already installed), new deps: `instaloader`, `shazamio`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `browser-cookie3`, `pytest`.

**Spec:** `C:\Users\Mbello\Desktop\ig-to-youtube-playlist\DESIGN.md`

## Global Constraints

- YouTube Data API quota: use `yt-dlp` (`ytsearch1:`) for finding videos (no quota cost); use the official API only for playlist reads/writes (`playlists.list/insert`, `playlistItems.insert`).
- No programmatic Instagram login: reuse the `sessionid`/`csrftoken` cookie already active in the user's Chrome; fall back to a manually-exported `cookies.txt` if that extraction fails.
- Processing is incremental via a local `processed.json`; re-runs must not re-process or duplicate anything already handled.
- Everything runs locally; nothing is uploaded to any third-party server beyond Instagram, Shazam-style recognition, YouTube search, and the YouTube API itself.
- Pace requests to Instagram (sleep between posts) to avoid tripping bot detection.
- Song identification tries every mode before giving up, in order: post metadata → audio fingerprint (`shazamio`) → caption/hashtag text guess — per explicit user instruction ("tenta usar tudo que é modo").
- Default playlist title: `"Músicas do Instagram"`.

## Review Focus

- A saved post with no video (photo-only) must be skipped and reported separately, never crash the run or land in "not identified". (Task 3)
- Instagram cookie extraction can fail (user logged out, or Chrome's cookie encryption blocks it) — must fail with a clear message pointing at the `cookies.txt` fallback, not a raw stack trace. (Task 2)
- The same song saved from two different Instagram posts must appear only once in the playlist — dedupe by resolved YouTube video id, not just by Instagram shortcode. (Task 7)
- A YouTube search with zero results must land the post in "not found on YouTube" and let the run continue, not abort the whole pipeline. (Task 5)
- Re-running the tool after a run that already processed everything must do nothing — no re-identification, no re-search, no duplicate API calls. (Task 8)

---

### Task 1: Project scaffolding & processed store

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `igtoyt/__init__.py`
- Create: `igtoyt/processed_store.py`
- Test: `tests/test_processed_store.py`

**Interfaces:**
- Produces:
  - `class ProcessedStore` with:
    - `ProcessedStore.load(path: Path) -> ProcessedStore` (empty store if file absent)
    - `.save(path: Path) -> None`
    - `.is_post_processed(shortcode: str) -> bool`
    - `.has_video(video_id: str) -> bool`
    - `.mark(shortcode: str, status: str, video_id: str | None) -> None`
  - `status` string values used by later tasks: `"added"`, `"guessed"`, `"skipped_photo"`, `"not_identified"`, `"not_found_on_youtube"`.

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests, verify they fail** (`pytest tests/test_processed_store.py -v`, expect `ModuleNotFoundError`)

- [ ] **Step 3: Implement `ProcessedStore` in `igtoyt/processed_store.py`**

Back it with a dict keyed by shortcode storing `{"status": str, "video_id": str | None}`, JSON-serialized. `has_video` scans stored entries for a matching `video_id`.

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Write `requirements.txt`**

Pin: `instaloader`, `shazamio`, `google-api-python-client`, `google-auth-oauthlib`, `google-auth-httplib2`, `browser-cookie3`, `pytest` (unpinned versions are fine for a personal tool; `yt-dlp` and `ffmpeg` are already present and not repeated here).

- [ ] **Step 6: Write `.gitignore`**

Ignore `processed.json`, `data/`, `token.json`, `client_secret.json`, `__pycache__/`, `*.pyc`.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .gitignore igtoyt/__init__.py igtoyt/processed_store.py tests/test_processed_store.py
git commit -m "feat: add processed-post store"
```

---

### Task 2: Instagram session authentication

**Files:**
- Create: `igtoyt/instagram_auth.py`
- Test: `tests/test_instagram_auth.py`

**Interfaces:**
- Produces:
  - `class CookieExtractionError(Exception)`
  - `extract_instagram_cookies_from_chrome() -> dict[str, str]` — returns `{"sessionid": ..., "csrftoken": ...}`; raises `CookieExtractionError` if either is missing or the underlying extraction raises.
  - `load_cookies_from_netscape_file(path: Path) -> dict[str, str]` — parses a Netscape-format `cookies.txt`, returns the same shape.
  - `build_authenticated_loader(cookies: dict[str, str]) -> instaloader.Instaloader` — injects the cookies into the loader's session.
  - `get_authenticated_loader(cookies_txt_path: Path | None = None, chrome_extractor=extract_instagram_cookies_from_chrome) -> instaloader.Instaloader` — tries `chrome_extractor()` first; on `CookieExtractionError`, falls back to `load_cookies_from_netscape_file(cookies_txt_path)` if given, else re-raises `CookieExtractionError` with a message naming the `cookies.txt` fallback described in `DESIGN.md`.

- [ ] **Step 1: Write failing tests**

```python
NETSCAPE_FIXTURE = """# Netscape HTTP Cookie File
.instagram.com\tTRUE\t/\tTRUE\t0\tsessionid\tSESSIDVALUE
.instagram.com\tTRUE\t/\tTRUE\t0\tcsrftoken\tCSRFVALUE
"""

def test_load_cookies_from_netscape_file(tmp_path):
    path = tmp_path / "cookies.txt"
    path.write_text(NETSCAPE_FIXTURE)
    cookies = load_cookies_from_netscape_file(path)
    assert cookies == {"sessionid": "SESSIDVALUE", "csrftoken": "CSRFVALUE"}

def test_get_authenticated_loader_raises_with_no_fallback():
    def failing_extractor():
        raise CookieExtractionError("no chrome cookie")
    with pytest.raises(CookieExtractionError, match="cookies.txt"):
        get_authenticated_loader(cookies_txt_path=None, chrome_extractor=failing_extractor)

def test_get_authenticated_loader_falls_back_to_file(tmp_path):
    path = tmp_path / "cookies.txt"
    path.write_text(NETSCAPE_FIXTURE)
    def failing_extractor():
        raise CookieExtractionError("no chrome cookie")
    loader = get_authenticated_loader(cookies_txt_path=path, chrome_extractor=failing_extractor)
    assert loader is not None
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `extract_instagram_cookies_from_chrome`**

Use `browser_cookie3.chrome(domain_name="instagram.com")`; pull `sessionid`/`csrftoken` by name from the resulting cookie jar; raise `CookieExtractionError` if either is absent or `browser_cookie3` itself raises.

- [ ] **Step 4: Implement `load_cookies_from_netscape_file`**

Standard Netscape cookie file: tab-separated fields, last two columns are name/value; keep only `sessionid`/`csrftoken`.

- [ ] **Step 5: Implement `build_authenticated_loader` and `get_authenticated_loader`**

Verify against the installed `instaloader` version exactly how to inject cookies into its session (e.g. `instaloader.Instaloader().context._session.cookies.set(...)` for each cookie) — this is the one fact to confirm against the live library rather than guess, since instaloader's internals can shift between versions.

- [ ] **Step 6: Run tests, verify they pass**

- [ ] **Step 7: Manual verification (not automated)**

Run (Chrome closed): `python -c "from igtoyt.instagram_auth import extract_instagram_cookies_from_chrome; print(extract_instagram_cookies_from_chrome())"`. Expected: prints a dict with real `sessionid`/`csrftoken` values. If it raises `CookieExtractionError`, this Chrome install needs the `cookies.txt` fallback — note that in the final report to the user rather than treating it as a bug.

- [ ] **Step 8: Commit**

```bash
git add igtoyt/instagram_auth.py tests/test_instagram_auth.py
git commit -m "feat: authenticate instaloader from the user's Chrome session"
```

---

### Task 3: Saved posts listing & download

**Files:**
- Create: `igtoyt/instagram_saved.py`
- Test: `tests/test_instagram_saved.py`

**Interfaces:**
- Consumes: `instaloader.Instaloader` from Task 2's `get_authenticated_loader()`.
- Produces:
  - `@dataclass SavedPost: shortcode: str; caption: str; hashtags: list[str]; is_video: bool; video_path: Path | None; audio_title: str | None; audio_artist: str | None`
  - `iter_saved_posts(loader: instaloader.Instaloader, download_dir: Path, delay_seconds: float = 3.0, posts_iterable=None) -> Iterator[SavedPost]` — iterates `posts_iterable` if given (test seam), else `instaloader.Profile.own_profile(loader.context).get_saved_posts()`; sleeps `delay_seconds` between posts; downloads video-only posts into `download_dir`; yields photo-only posts with `is_video=False, video_path=None` and skips downloading them; reads `audio_title`/`audio_artist` off the post's music-attribution field when instaloader exposes one for that post, else leaves both `None`.

- [ ] **Step 1: Write failing tests**

```python
class FakePost:
    def __init__(self, shortcode, caption, hashtags, is_video, music=None):
        self.shortcode = shortcode
        self.caption = caption
        self.caption_hashtags = hashtags
        self.is_video = is_video
        self._music = music  # test double for whatever field Step 5 ends up reading

def test_photo_post_is_skipped_not_downloaded(tmp_path, monkeypatch):
    post = FakePost("abc", "a caption", ["tag1"], is_video=False)
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].is_video is False
    assert results[0].video_path is None

def test_video_post_with_music_attribution(tmp_path, monkeypatch):
    post = FakePost("def", "caption", [], is_video=True, music={"song_name": "Song", "artist_name": "Artist"})
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].audio_title == "Song"
    assert results[0].audio_artist == "Artist"

def test_video_post_without_music_attribution_has_none_fields(tmp_path):
    post = FakePost("ghi", "caption", [], is_video=True, music=None)
    results = list(iter_saved_posts(loader=None, download_dir=tmp_path, delay_seconds=0, posts_iterable=[post]))
    assert results[0].audio_title is None
    assert results[0].audio_artist is None
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `SavedPost` and `iter_saved_posts`**

Download video posts via the real `loader` only when `posts_iterable` is not supplied (keeps the tests network-free). Confirm the actual instaloader field/method for music attribution against the installed version while implementing; if no such field exists in this version, leave `audio_title`/`audio_artist` `None` for every post (Task 4's cascade still works — it just always falls through metadata).

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Commit**

```bash
git add igtoyt/instagram_saved.py tests/test_instagram_saved.py
git commit -m "feat: list and download saved Instagram posts"
```

---

### Task 4: Song identification cascade

**Files:**
- Create: `igtoyt/identify_song.py`
- Test: `tests/test_identify_song.py`

**Interfaces:**
- Consumes: `SavedPost` from Task 3.
- Produces:
  - `@dataclass SongMatch: query: str; title: str | None; artist: str | None; method: Literal["metadata", "fingerprint", "caption_guess"]; confidence: Literal["exact", "guess"]`
  - `identify_from_metadata(post: SavedPost) -> SongMatch | None` — `"exact"` match when both `post.audio_title` and `post.audio_artist` are set, else `None`.
  - `identify_from_audio_fingerprint(video_path: Path, recognizer) -> SongMatch | None` — extracts audio to a temp file via `ffmpeg` (subprocess), calls `recognizer(audio_path) -> dict | None`; `"exact"` match built from the recognizer's track title/artist when it returns a dict, else `None`.
  - `identify_from_caption(post: SavedPost) -> SongMatch | None` — `"guess"` match whose `query` is the cleaned caption + hashtags text; `None` only when caption and hashtags are both empty.
  - `identify_song(post: SavedPost, video_path: Path | None, recognizer) -> SongMatch | None` — tries metadata, then (if `video_path` is not `None`) fingerprint, then caption, in that order; returns the first non-`None` result.
  - `shazamio_recognize(audio_path: Path) -> dict | None` — real default `recognizer`, wraps `shazamio.Shazam().recognize(str(audio_path))` via `asyncio.run`.

- [ ] **Step 1: Write failing tests for `identify_from_metadata`**

```python
def test_metadata_match_when_both_fields_present():
    post = SavedPost("a", "", [], True, None, audio_title="Song", audio_artist="Artist")
    match = identify_from_metadata(post)
    assert match.confidence == "exact" and match.method == "metadata"

def test_metadata_none_when_either_field_missing():
    post = SavedPost("a", "", [], True, None, audio_title="Song", audio_artist=None)
    assert identify_from_metadata(post) is None
```

- [ ] **Step 2: Write failing tests for `identify_from_audio_fingerprint`**

```python
def test_fingerprint_match_when_recognizer_finds_track(tmp_path):
    video = tmp_path / "v.mp4"; video.write_bytes(b"")
    match = identify_from_audio_fingerprint(video, recognizer=lambda p: {"title": "Song", "artist": "Artist"})
    assert match.confidence == "exact" and match.method == "fingerprint"

def test_fingerprint_none_when_recognizer_finds_nothing(tmp_path):
    video = tmp_path / "v.mp4"; video.write_bytes(b"")
    assert identify_from_audio_fingerprint(video, recognizer=lambda p: None) is None
```

- [ ] **Step 3: Write failing tests for `identify_from_caption`**

```python
def test_caption_guess_built_from_caption_and_hashtags():
    post = SavedPost("a", "ótima vibe", ["musica", "throwback"], True, None, None, None)
    match = identify_from_caption(post)
    assert match.confidence == "guess" and match.method == "caption_guess"

def test_caption_none_when_caption_and_hashtags_empty():
    post = SavedPost("a", "", [], True, None, None, None)
    assert identify_from_caption(post) is None
```

- [ ] **Step 4: Write failing tests for `identify_song` cascade order**

```python
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
```

- [ ] **Step 5: Run tests, verify they fail**

- [ ] **Step 6: Implement all four `identify_*` functions and `identify_song`**

- [ ] **Step 7: Run tests, verify they pass**

- [ ] **Step 8: Implement `shazamio_recognize`**

No automated test for this one — it is the real network-calling default and is exercised only through Task 4's injected `recognizer` seam elsewhere. Smoke-test it manually once with a short local audio clip and note the result.

- [ ] **Step 9: Commit**

```bash
git add igtoyt/identify_song.py tests/test_identify_song.py
git commit -m "feat: identify saved-post songs via metadata, fingerprint, or caption guess"
```

---

### Task 5: YouTube search via yt-dlp

**Files:**
- Create: `igtoyt/youtube_search.py`
- Test: `tests/test_youtube_search.py`

**Interfaces:**
- Consumes: `SongMatch.query` from Task 4.
- Produces:
  - `@dataclass VideoResult: video_id: str; title: str; url: str`
  - `search_youtube(query: str, ytdlp_extractor) -> VideoResult | None` — calls `ytdlp_extractor(query) -> dict`; returns `None` if the extractor raises or returns no `"entries"`; else maps the first entry to `VideoResult`.
  - `real_ytdlp_extractor(query: str) -> dict` — the production `ytdlp_extractor`, wraps `yt_dlp.YoutubeDL({"quiet": True}).extract_info(f"ytsearch1:{query}", download=False)`.

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `VideoResult`, `search_youtube`, `real_ytdlp_extractor`**

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Commit**

```bash
git add igtoyt/youtube_search.py tests/test_youtube_search.py
git commit -m "feat: search YouTube via yt-dlp without burning API quota"
```

---

### Task 6: YouTube OAuth client

**Files:**
- Create: `igtoyt/youtube_auth.py`
- Test: `tests/test_youtube_auth.py`

**Interfaces:**
- Produces:
  - `get_youtube_client(client_secret_path: Path, token_path: Path, credentials_loader, flow_runner, api_builder) -> Any` — if `token_path` holds credentials via `credentials_loader(token_path)` and they're valid, calls `api_builder(creds)` directly; if expired but refreshable, calls `.refresh()` then `api_builder(creds)` and re-saves to `token_path`; else calls `flow_runner(client_secret_path)` to get fresh credentials, saves them to `token_path`, then `api_builder(creds)`.
  - `real_credentials_loader`, `real_flow_runner`, `real_api_builder` — the production defaults wrapping `google.oauth2.credentials.Credentials`, `google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(...).run_local_server()`, and `googleapiclient.discovery.build("youtube", "v3", credentials=creds)` respectively.

- [ ] **Step 1: Write failing tests**

```python
class FakeCreds:
    def __init__(self, valid, expired=False, refresh_token=None):
        self.valid, self.expired, self.refresh_token = valid, expired, refresh_token
        self.refreshed = False
    def refresh(self, request): self.refreshed = True; self.valid = True

def test_uses_cached_valid_credentials(tmp_path):
    creds = FakeCreds(valid=True)
    client = get_youtube_client(tmp_path / "secret.json", tmp_path / "token.json",
        credentials_loader=lambda p: creds, flow_runner=lambda p: (_ for _ in ()).throw(AssertionError("should not run flow")),
        api_builder=lambda c: "built-client")
    assert client == "built-client"

def test_refreshes_expired_credentials_with_refresh_token(tmp_path):
    creds = FakeCreds(valid=False, expired=True, refresh_token="rt")
    get_youtube_client(tmp_path / "secret.json", tmp_path / "token.json",
        credentials_loader=lambda p: creds, flow_runner=lambda p: (_ for _ in ()).throw(AssertionError("should not run flow")),
        api_builder=lambda c: c)
    assert creds.refreshed is True

def test_runs_flow_when_no_cached_credentials(tmp_path):
    new_creds = FakeCreds(valid=True)
    called = {"flow": False}
    def flow_runner(p): called["flow"] = True; return new_creds
    get_youtube_client(tmp_path / "secret.json", tmp_path / "token.json",
        credentials_loader=lambda p: None, flow_runner=flow_runner, api_builder=lambda c: c)
    assert called["flow"] is True
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `get_youtube_client` and the three real-default wrappers**

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Commit**

```bash
git add igtoyt/youtube_auth.py tests/test_youtube_auth.py
git commit -m "feat: add cached/refreshable YouTube OAuth client"
```

> One-time manual prerequisite (not code): a Google Cloud project with the YouTube Data API v3 enabled and an OAuth "Desktop app" client, saved as `client_secret.json` next to the project. Documented as a setup step in Task 8's README, not implemented as code here.

---

### Task 7: YouTube playlist operations

**Files:**
- Create: `igtoyt/youtube_playlist.py`
- Test: `tests/test_youtube_playlist.py`

**Interfaces:**
- Consumes: YouTube client from Task 6, `VideoResult` from Task 5, `ProcessedStore` from Task 1.
- Produces:
  - `ensure_playlist(youtube, title: str) -> str` — finds an existing playlist owned by the user whose title matches `title` (case-insensitive) via `playlists().list(mine=True, part="snippet", maxResults=50).execute()`; returns its id, else creates one via `playlists().insert(...)` and returns the new id.
  - `add_video_to_playlist(youtube, playlist_id: str, video_id: str, store: ProcessedStore) -> bool` — returns `False` without any API call if `store.has_video(video_id)`; else calls `playlistItems().insert(...)` and returns `True`.

- [ ] **Step 1: Write failing tests**

```python
class FakeYouTube:
    def __init__(self, existing_playlists=(), insert_result="new-id"):
        self._existing = existing_playlists
        self._insert_result = insert_result
        self.insert_called = False
    def playlists(self): return self
    def list(self, **kw): return self
    def insert(self, **kw): self.insert_called = True; return self
    def execute(self):
        if self.insert_called: return {"id": self._insert_result}
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
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `ensure_playlist` and `add_video_to_playlist`**

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Commit**

```bash
git add igtoyt/youtube_playlist.py tests/test_youtube_playlist.py
git commit -m "feat: create/reuse playlist and insert videos with dedupe"
```

---

### Task 8: Orchestration, report, and setup README

**Files:**
- Create: `igtoyt/main.py`
- Create: `README.md`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: everything from Tasks 1–7.
- Produces:
  - `@dataclass Report: added: list[str]; guessed: list[str]; skipped_photos: list[str]; not_identified: list[str]; not_found_on_youtube: list[str]`
  - `run_pipeline(store, youtube, playlist_id, download_dir, saved_posts, identify, search, add_to_playlist) -> Report` — for each `post` in `saved_posts` where `not store.is_post_processed(post.shortcode)`: if not `post.is_video` → append to `skipped_photos`, `store.mark(..., "skipped_photo", None)`, continue; else `match = identify(post, post.video_path)`; if `match is None` → `not_identified`, `store.mark(..., "not_identified", None)`, continue; `video = search(match.query)`; if `video is None` → `not_found_on_youtube`, `store.mark(..., "not_found_on_youtube", None)`, continue; `add_to_playlist(youtube, playlist_id, video.video_id, store)`; append to `added` if `match.confidence == "exact"` else `guessed`; `store.mark(..., match.confidence == "exact" and "added" or "guessed", video.video_id)`. Calls `store.save(...)` once after the loop.
  - `main() -> None` — wires the real functions from Tasks 2–7 with `playlist_id = ensure_playlist(youtube, "Músicas do Instagram")`, loads/saves the real `ProcessedStore`, calls `run_pipeline`, prints the `Report` counts.

- [ ] **Step 1: Write failing tests**

```python
def make_post(shortcode, is_video=True):
    return SavedPost(shortcode, "", [], is_video, None, None, None)

def test_already_processed_post_is_skipped(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    store.mark("done1", status="added", video_id="vidX")
    calls = {"identify": 0}
    def identify(post, path): calls["identify"] += 1; return None
    run_pipeline(store, youtube=None, playlist_id="p", download_dir=Path("."),
        saved_posts=[make_post("done1")], identify=identify,
        search=lambda q: None, add_to_playlist=lambda *a: True)
    assert calls["identify"] == 0

def test_photo_post_recorded_as_skipped(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    report = run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("photo1", is_video=False)],
        identify=lambda post, path: None, search=lambda q: None, add_to_playlist=lambda *a: True)
    assert report.skipped_photos == ["photo1"]

def test_unidentified_post_recorded(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    report = run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("v1")], identify=lambda post, path: None,
        search=lambda q: None, add_to_playlist=lambda *a: True)
    assert report.not_identified == ["v1"]

def test_identified_but_not_found_on_youtube(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    match = SongMatch(query="x", title="t", artist="a", method="metadata", confidence="exact")
    report = run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("v2")], identify=lambda post, path: match,
        search=lambda q: None, add_to_playlist=lambda *a: True)
    assert report.not_found_on_youtube == ["v2"]

def test_exact_match_added_guess_match_guessed(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    video = VideoResult("vid1", "t", "u")
    exact = SongMatch(query="x", title="t", artist="a", method="metadata", confidence="exact")
    guess = SongMatch(query="x", title=None, artist=None, method="caption_guess", confidence="guess")
    report = run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("v3")], identify=lambda post, path: exact,
        search=lambda q: video, add_to_playlist=lambda *a: True)
    assert report.added == ["v3"]
    report2 = run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("v4")], identify=lambda post, path: guess,
        search=lambda q: video, add_to_playlist=lambda *a: True)
    assert report2.guessed == ["v4"]

def test_rerun_with_everything_processed_touches_nothing(tmp_path):
    store = ProcessedStore.load(tmp_path / "p.json")
    store.mark("v5", status="added", video_id="vid1")
    calls = {"n": 0}
    def identify(post, path): calls["n"] += 1; return None
    run_pipeline(store, youtube=None, playlist_id="p", download_dir=tmp_path,
        saved_posts=[make_post("v5")], identify=identify, search=lambda q: None, add_to_playlist=lambda *a: True)
    assert calls["n"] == 0
```

- [ ] **Step 2: Run tests, verify they fail**

- [ ] **Step 3: Implement `Report` and `run_pipeline`**

- [ ] **Step 4: Run tests, verify they pass**

- [ ] **Step 5: Implement `main()`**

Wire the real `get_authenticated_loader`, `iter_saved_posts`, `identify_song` (with `shazamio_recognize`), `search_youtube` (with `real_ytdlp_extractor`), `get_youtube_client`, `ensure_playlist`, `add_video_to_playlist`, and `ProcessedStore`. Constants at the top of the file: playlist title `"Músicas do Instagram"`, `download_dir`, `client_secret.json`/`token.json`/`processed.json` paths. Print the `Report` counts at the end.

- [ ] **Step 6: Write `README.md`**

Cover: `pip install -r requirements.txt`; the one-time Google Cloud setup (create project, enable YouTube Data API v3, create an OAuth "Desktop app" client, save as `client_secret.json`) — noting this can be done by walking through Google Cloud Console in the browser the user already has open, per `DESIGN.md`; the "Chrome should be closed" caveat for cookie extraction and the `cookies.txt` fallback; how to run (`python -m igtoyt.main`); where the final report prints.

- [ ] **Step 7: Commit**

```bash
git add igtoyt/main.py README.md tests/test_main.py
git commit -m "feat: wire the full Instagram-to-YouTube pipeline with a summary report"
```
