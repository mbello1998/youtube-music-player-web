from pathlib import Path

import instaloader
import yt_dlp.cookies


class CookieExtractionError(Exception):
    pass


def extract_instagram_cookies_from_chrome() -> dict[str, str]:
    try:
        jar = yt_dlp.cookies.extract_cookies_from_browser("chrome")
    except Exception as exc:
        raise CookieExtractionError(f"could not read Chrome cookies: {exc}") from exc

    cookies = {
        cookie.name: cookie.value
        for cookie in jar
        if cookie.domain and "instagram.com" in cookie.domain
    }
    if "sessionid" not in cookies:
        raise CookieExtractionError(
            "Instagram sessionid not found in Chrome cookies "
            "(are you logged into instagram.com in Chrome?)"
        )
    return cookies


def load_cookies_from_netscape_file(path: Path) -> dict[str, str]:
    """Parse a Netscape cookie file and return instagram.com cookies."""
    cookies: dict[str, str] = {}
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 7:
                continue
            domain, name, value = fields[0], fields[5], fields[6]
            if "instagram.com" in domain:
                cookies[name] = value
    if "sessionid" not in cookies:
        raise CookieExtractionError(
            "sessionid not found in cookies.txt — make sure you exported "
            "cookies from instagram.com while logged in."
        )
    return cookies


def build_authenticated_loader(cookies: dict[str, str]) -> instaloader.Instaloader:
    """Inject cookies directly into instaloader's requests session."""
    loader = instaloader.Instaloader()
    loader.context._session.cookies.clear()
    for name, value in cookies.items():
        loader.context._session.cookies.set(name, value, domain=".instagram.com")
    loader.context.username = cookies.get("ds_user_id", "instagram_user")
    return loader


def get_authenticated_loader(
    cookies_txt_path: Path | None = None,
    chrome_extractor=extract_instagram_cookies_from_chrome,
) -> instaloader.Instaloader:
    try:
        cookies = chrome_extractor()
    except CookieExtractionError:
        if cookies_txt_path is None:
            raise CookieExtractionError(
                "Could not read the Instagram session from Chrome. "
                "Export a cookies.txt (e.g. with the 'Get cookies.txt LOCALLY' "
                "Chrome extension, as described in DESIGN.md) and pass its path."
            )
        cookies = load_cookies_from_netscape_file(cookies_txt_path)

    return build_authenticated_loader(cookies)
