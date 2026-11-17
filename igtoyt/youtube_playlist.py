import time
from igtoyt.processed_store import ProcessedStore


def ensure_playlist(youtube, title: str) -> str:
    response = youtube.playlists().list(mine=True, part="snippet", maxResults=50).execute()
    for item in response.get("items", []):
        if item["snippet"]["title"].lower() == title.lower():
            return item["id"]

    created = (
        youtube.playlists()
        .insert(
            part="snippet",
            body={"snippet": {"title": title}},
        )
        .execute()
    )
    return created["id"]


def add_video_to_playlist(youtube, playlist_id: str, video_id: str, store: ProcessedStore) -> bool:
    if store.has_video(video_id):
        return False

    for attempt in range(3):
        try:
            youtube.playlistItems().insert(
                part="snippet",
                body={"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}},
            ).execute()
            return True
        except Exception:
            if attempt < 2:
                time.sleep(2)
                continue
            raise
    return False
