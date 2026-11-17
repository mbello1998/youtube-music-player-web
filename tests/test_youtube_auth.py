from igtoyt.youtube_auth import get_youtube_client


class FakeCreds:
    def __init__(self, valid, expired=False, refresh_token=None):
        self.valid, self.expired, self.refresh_token = valid, expired, refresh_token
        self.refreshed = False

    def refresh(self, request):
        self.refreshed = True
        self.valid = True

    def to_json(self):
        return "{}"


def test_uses_cached_valid_credentials(tmp_path):
    creds = FakeCreds(valid=True)
    client = get_youtube_client(
        tmp_path / "secret.json",
        tmp_path / "token.json",
        credentials_loader=lambda p: creds,
        flow_runner=lambda p: (_ for _ in ()).throw(AssertionError("should not run flow")),
        api_builder=lambda c: "built-client",
    )
    assert client == "built-client"


def test_refreshes_expired_credentials_with_refresh_token(tmp_path):
    creds = FakeCreds(valid=False, expired=True, refresh_token="rt")
    get_youtube_client(
        tmp_path / "secret.json",
        tmp_path / "token.json",
        credentials_loader=lambda p: creds,
        flow_runner=lambda p: (_ for _ in ()).throw(AssertionError("should not run flow")),
        api_builder=lambda c: c,
    )
    assert creds.refreshed is True


def test_runs_flow_when_no_cached_credentials(tmp_path):
    new_creds = FakeCreds(valid=True)
    called = {"flow": False}

    def flow_runner(p):
        called["flow"] = True
        return new_creds

    get_youtube_client(
        tmp_path / "secret.json",
        tmp_path / "token.json",
        credentials_loader=lambda p: None,
        flow_runner=flow_runner,
        api_builder=lambda c: c,
    )
    assert called["flow"] is True
