from pathlib import Path
from typing import Any

YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube"]


def real_credentials_loader(token_path: Path):
    from google.oauth2.credentials import Credentials

    if not Path(token_path).exists():
        return None
    return Credentials.from_authorized_user_file(str(token_path), YOUTUBE_SCOPES)


def real_flow_runner(client_secret_path: Path):
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret_path), YOUTUBE_SCOPES)
    return flow.run_local_server()


def real_api_builder(creds):
    from googleapiclient.discovery import build

    return build("youtube", "v3", credentials=creds)


def _save_credentials(creds, token_path: Path) -> None:
    Path(token_path).write_text(creds.to_json())


def get_youtube_client(
    client_secret_path: Path,
    token_path: Path,
    credentials_loader=real_credentials_loader,
    flow_runner=real_flow_runner,
    api_builder=real_api_builder,
) -> Any:
    creds = credentials_loader(token_path)

    if creds and creds.valid:
        return api_builder(creds)

    if creds and creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request

        creds.refresh(Request())
        _save_credentials(creds, token_path)
        return api_builder(creds)

    creds = flow_runner(client_secret_path)
    _save_credentials(creds, token_path)
    return api_builder(creds)
