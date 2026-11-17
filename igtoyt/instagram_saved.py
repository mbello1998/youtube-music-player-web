import http.cookiejar
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Optional

import instaloader
from playwright.sync_api import sync_playwright


@dataclass
class SavedPost:
    shortcode: str
    caption: str
    hashtags: list[str]
    is_video: bool
    video_path: Optional[Path]
    audio_title: Optional[str]
    audio_artist: Optional[str]


def _extract_playwright_cookies(cookies_txt_path: Path) -> list[dict]:
    jar = http.cookiejar.MozillaCookieJar(str(cookies_txt_path))
    jar.load(ignore_discard=True, ignore_expires=True)
    playwright_cookies = []
    for c in jar:
        if "instagram.com" in (c.domain or ""):
            cookie_dict = {
                "name": c.name,
                "value": c.value,
                "domain": c.domain,
                "path": c.path,
                "secure": c.secure,
            }
            if c.expires:
                cookie_dict["expires"] = float(c.expires)
            playwright_cookies.append(cookie_dict)
    return playwright_cookies


def _fetch_saved_audios_via_playwright(
    cookies_txt_path: Path, max_scrolls: int = 150
) -> list[dict]:
    """Deep-scroll instagram.com/<username>/saved/audio/ to retrieve 100% of saved songs."""
    cache_path = Path("saved_audios_all.json")
    if cache_path.exists():
        try:
            with cache_path.open("r", encoding="utf-8") as f:
                cached = json.load(f)
                if len(cached) >= 100:
                    print(f"Carregando {len(cached)} músicas salvas do catálogo...")
                    return cached
        except Exception:
            pass

    playwright_cookies = _extract_playwright_cookies(cookies_txt_path)
    print("Conectando ao Instagram para carregar TODAS as suas MÚSICAS SALVAS (saved/audio)...")

    seen: dict[str, dict] = {}
    stagnant_rounds = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            )
        )
        context.add_cookies(playwright_cookies)
        page = context.new_page()

        saved_audio_url = "https://www.instagram.com/matheus.b.p/saved/audio/"
        page.goto(saved_audio_url, wait_until="networkidle")

        for _ in range(max_scrolls):
            anchors = page.query_selector_all('a[href*="/reels/audio/"]')
            for a in anchors:
                href = a.get_attribute("href") or ""
                m = re.search(r"/reels/audio/(\d+)/", href)
                if not m:
                    continue
                audio_id = m.group(1)
                if audio_id in seen:
                    continue

                text = a.inner_text().strip()
                parent = a.evaluate_handle('el => el.closest("div[role=button], li, div")')
                parent_text = (
                    parent.as_element().inner_text()
                    if parent and parent.as_element()
                    else ""
                )
                lines = [
                    line.strip()
                    for line in parent_text.split("\n")
                    if line.strip() and line.strip() != "•" and not re.match(r"^\d+:\d+$", line.strip())
                ]

                title = text or (lines[0] if lines else f"Audio_{audio_id}")
                artist = ""
                if len(lines) > 1 and lines[0] == title:
                    artist = lines[1]
                elif len(lines) > 0 and lines[0] != title:
                    artist = lines[0]

                if title.lower() == "original audio" and artist:
                    title = f"Áudio original de {artist}"

                seen[audio_id] = {
                    "id": audio_id,
                    "title": title,
                    "artist": artist,
                    "url": href,
                }

            before = len(seen)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            page.evaluate("window.scrollBy(0, -400)")
            page.wait_for_timeout(500)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1500)

            if len(seen) == before:
                stagnant_rounds += 1
                if stagnant_rounds >= 6:
                    break
            else:
                stagnant_rounds = 0

        browser.close()

    audios = list(seen.values())
    try:
        with cache_path.open("w", encoding="utf-8") as f:
            json.dump(audios, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    print(f"Total definitivo de MÚSICAS SALVAS encontradas: {len(audios)}")
    return audios


def iter_saved_posts(
    loader: Optional[instaloader.Instaloader],
    download_dir: Path,
    delay_seconds: float = 1.0,
    posts_iterable=None,
    cookies_txt_path: Optional[Path] = None,
) -> Iterator[SavedPost]:
    if posts_iterable is not None:
        for post in posts_iterable:
            audio_title = audio_artist = None
            metadata = getattr(post, "_full_metadata", {}) or {}
            music = metadata.get("clips_music_attribution_info") or {}
            if music:
                audio_title = music.get("song_name")
                audio_artist = music.get("artist_name")
            yield SavedPost(
                shortcode=post.shortcode,
                caption=post.caption or "",
                hashtags=list(post.caption_hashtags),
                is_video=post.is_video,
                video_path=None,
                audio_title=audio_title,
                audio_artist=audio_artist,
            )
        return

    c_path = cookies_txt_path or Path("cookies.txt")
    audios = _fetch_saved_audios_via_playwright(c_path)

    for item in audios:
        yield SavedPost(
            shortcode=item["id"],
            caption="",
            hashtags=[],
            is_video=True,
            video_path=None,
            audio_title=item["title"],
            audio_artist=item["artist"] or None,
        )
        if delay_seconds:
            time.sleep(delay_seconds)
