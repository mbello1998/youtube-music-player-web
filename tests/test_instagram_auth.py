import pytest

from igtoyt.instagram_auth import (
    CookieExtractionError,
    get_authenticated_loader,
    load_cookies_from_netscape_file,
)

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
