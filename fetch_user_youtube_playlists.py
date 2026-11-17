import json
import yt_dlp

playlists = [
    ('Sertanejo Antigo', 'PLRVygSlnKIdZSE4zZ_k44nFSVy5I1q5sA'),
    ('Reggaeton', 'PLRVygSlnKIdZEcyfpS1eanCLQV4vnZRXj'),
    ('Sertanejo', 'PLRVygSlnKIdZnCyCZa3mZdwpSYDHLfReL'),
    ('Samba/Pagode', 'PLRVygSlnKIdZtCEaRoqiu4gethtfktBig'),
    ('Supermix festa', 'PLRVygSlnKIda35BpDbnNwN37nW_870xcZ'),
    ('leves', 'PLRVygSlnKIdY-PcyXme-uju4ilW6JMCPp'),
    ('músicas aleatórias', 'PLRVygSlnKIdYI8Llrr562MDpmJyem-tWk'),
]

all_yt_tracks = {}

ydl_opts = {
    "extract_flat": True,
    "quiet": True,
    "skip_download": True,
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for name, pid in playlists:
        url = f"https://www.youtube.com/playlist?list={pid}"
        try:
            info = ydl.extract_info(url, download=False)
            entries = info.get("entries") or []
            print(f"[{name}] ({pid}): {len(entries)} faixas encontradas")
            track_list = []
            for e in entries:
                t_title = e.get("title")
                v_id = e.get("id")
                if t_title and v_id:
                    track_list.append({"title": t_title, "video_id": v_id})
            all_yt_tracks[name] = track_list
        except Exception as err:
            print(f"[{name}] ({pid}): erro/privada: {err}")

with open("user_youtube_playlists.json", "w", encoding="utf-8") as f:
    json.dump(all_yt_tracks, f, ensure_ascii=False, indent=2)

print("\nConcluído! Salvo em user_youtube_playlists.json")
