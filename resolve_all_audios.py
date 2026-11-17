import json
import time
from pathlib import Path
from igtoyt.categorize import categorize_song
from igtoyt.youtube_search import search_youtube, real_ytdlp_extractor

with open("saved_audios_all.json", "r", encoding="utf-8") as f:
    audios = json.load(f)

proc = {}
if Path("processed.json").exists():
    with open("processed.json", "r", encoding="utf-8") as f:
        proc = json.load(f)

resolved_path = Path("audio_catalog_resolved.json")
resolved_catalog = {}
if resolved_path.exists():
    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            resolved_catalog = json.load(f)
    except Exception:
        resolved_catalog = {}

print(f"Total de músicas a catalogar: {len(audios)}")
print(f"Já resolvidas previamente: {len(resolved_catalog)}")

for i, a in enumerate(audios, 1):
    audio_id = a["id"]
    title = a.get("title") or ""
    artist = a.get("artist") or ""
    category = categorize_song(title, artist)

    if audio_id in resolved_catalog and resolved_catalog[audio_id].get("video_id"):
        # Garante categoria atualizada
        resolved_catalog[audio_id]["category"] = category
        continue

    # Checa se já estava no processed.json antigo
    if audio_id in proc and proc[audio_id].get("video_id"):
        video_id = proc[audio_id]["video_id"]
        resolved_catalog[audio_id] = {
            "id": audio_id,
            "title": title,
            "artist": artist,
            "category": category,
            "video_id": video_id,
            "yt_title": proc[audio_id].get("video_id"),
        }
        continue

    # Busca via yt-dlp
    query = f"{title} {artist}".strip()
    if title.lower() == "original audio":
        query = f"musica {artist}".strip()

    res = search_youtube(query, real_ytdlp_extractor)
    if res:
        resolved_catalog[audio_id] = {
            "id": audio_id,
            "title": title,
            "artist": artist,
            "category": category,
            "video_id": res.video_id,
            "yt_title": res.title,
            "yt_url": res.url,
        }
        print(f"[{i:3d}/{len(audios)}] [OK] [{category}] {title} - {artist} -> {res.title}")
    else:
        resolved_catalog[audio_id] = {
            "id": audio_id,
            "title": title,
            "artist": artist,
            "category": category,
            "video_id": None,
            "yt_title": None,
        }
        print(f"[{i:3d}/{len(audios)}] [FALHA] {title} - {artist}")

    # Salva periodicamente
    if i % 10 == 0:
        with open(resolved_path, "w", encoding="utf-8") as f:
            json.dump(resolved_catalog, f, ensure_ascii=False, indent=2)

with open(resolved_path, "w", encoding="utf-8") as f:
    json.dump(resolved_catalog, f, ensure_ascii=False, indent=2)

total_found = sum(1 for v in resolved_catalog.values() if v.get("video_id"))
print(f"\nFinalizado! Total com vídeo encontrado no YouTube: {total_found}/{len(audios)}")
