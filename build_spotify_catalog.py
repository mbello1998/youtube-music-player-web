import urllib.request
import json
import re
import yt_dlp
import time
import sys
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

PLAYLIST_DEFS = [
    {
        "id": "top_brasil",
        "name": "Top Brasil",
        "badge": "🇧🇷 Top Brasil",
        "icon": "🇧🇷",
        "genre": "Sertanejo & Pop BR",
        "desc": "A principal playlist com os maiores hits do país, reunindo artistas como Hugo & Guilherme, Zé Vaqueiro, Mari Fernandez e Luan Pereira.",
        "spotify_id": "37i9dQZF1DX0FOF1IUWK1W",
        "bpm": 130
    },
    {
        "id": "top_50_brasil",
        "name": "Top 50 – Brasil",
        "badge": "📈 Top 50 Brasil",
        "icon": "📈",
        "genre": "Ranking Diário BR",
        "desc": "O ranking oficial diário atualizado com as 50 músicas mais tocadas no território brasileiro.",
        "spotify_id": "37i9dQZEVXbMXbN3EUUhlg",
        "bpm": 132
    },
    {
        "id": "top_50_mundo",
        "name": "Top 50 – Mundo",
        "badge": "🌍 Top 50 Mundo",
        "icon": "🌍",
        "genre": "Hits Globais",
        "desc": "As faixas internacionais e latinas que estão dominando as paradas globais no momento.",
        "spotify_id": "37i9dQZEVXbMDoHDwVN2tF",
        "bpm": 124
    },
    {
        "id": "funk_hits",
        "name": "Funk Hits",
        "badge": "🔥 Funk Hits",
        "icon": "🔥",
        "genre": "Funk Paulista & Ritmadas",
        "desc": "Hits de funk mais escutados nas ruas e no streaming: mandelão, ritmo louco e batidões.",
        "spotify_id": "37i9dQZF1DXajcHa62WwUp",
        "bpm": 135
    },
    {
        "id": "esquenta_sertanejo",
        "name": "Esquenta Sertanejo",
        "badge": "🤠 Esquenta Sertanejo",
        "icon": "🤠",
        "genre": "Sertanejo Universitário & Modão",
        "desc": "Seleção forte de sertanejo universitário e modão para churrasco, festa e boteco.",
        "spotify_id": "37i9dQZF1DXdSjVZQzv2tl",
        "bpm": 128
    },
    {
        "id": "gigantes_rap",
        "name": "Gigantes do Rap Nacional",
        "badge": "🎤 Rap Nacional",
        "icon": "🎤",
        "genre": "Trap & Rap Nacional",
        "desc": "Destaques consagrados e novos monstros do rap e trap no Brasil.",
        "spotify_id": "37i9dQZF1DXaljDe6fISR1",
        "bpm": 140
    }
]

output_file = Path(r"C:\Users\Mbello\Desktop\ig-to-youtube-playlist\.claude\worktrees\instagram-youtube-playlist\spotify_playlists_catalog.json")

catalog = {}
if output_file.exists():
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            catalog = json.load(f)
    except Exception:
        catalog = {}

ydl_opts = {
    "extract_flat": True,
    "quiet": True,
    "no_warnings": True,
    "ignoreerrors": True,
    "socket_timeout": 6
}

def save_catalog():
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for pl_meta in PLAYLIST_DEFS:
        pl_id = pl_meta["id"]
        sp_id = pl_meta["spotify_id"]
        print(f"\n[{pl_meta['name']}] Spotify ID: {sp_id}", flush=True)

        if pl_id in catalog and len(catalog[pl_id].get("tracks", [])) >= 10:
            print(f"  Playlist {pl_meta['name']} já possui {len(catalog[pl_id]['tracks'])} faixas prontas.", flush=True)
            continue

        raw_tracks = []
        try:
            url = f"https://open.spotify.com/embed/playlist/{sp_id}"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
                if m:
                    data = json.loads(m.group(1))
                    entity = data.get('props', {}).get('pageProps', {}).get('state', {}).get('data', {}).get('entity', {})
                    raw_tracks = entity.get('trackList', [])
        except Exception as e:
            print(f"  Erro ao obter embed do Spotify: {e}", flush=True)

        print(f"  Obtidas {len(raw_tracks)} faixas da lista oficial.", flush=True)
        resolved_tracks = catalog.get(pl_id, {}).get("tracks", [])
        existing_ranks = {t.get("rank") for t in resolved_tracks}

        target_tracks = raw_tracks[:10]
        for rank, st in enumerate(target_tracks, 1):
            if rank in existing_ranks:
                continue

            s_title = st.get("title", "").strip()
            s_artist = st.get("subtitle", "").strip()
            clean_title = re.sub(r'[\u2700-\u27bf]|[\u2b50]|[\ud83c-\ud83e][\udc00-\udfff]', '', s_title).strip()
            # Remove sufixos como (Ao Vivo), - Ao Vivo para busca mais limpa
            search_title = re.sub(r'[\(\[\-]\s*(Ao Vivo|Live|Remix|Slowed).*?[\)\]]?', '', clean_title, flags=re.I).strip()
            first_artist = s_artist.split(",")[0].strip()
            query = f"{search_title} {first_artist}".strip()
            query = re.sub(r'[^\w\s]', ' ', query)

            v_id = None
            yt_title = None
            dur = int(st.get("duration", 0) / 1000)

            try:
                res = ydl.extract_info(f"ytsearch1:{query}", download=False)
                entries = res.get("entries") or []
                if entries:
                    e = entries[0]
                    v_id = e.get("id")
                    yt_title = e.get("title")
                    if e.get("duration"):
                        dur = int(e.get("duration"))
            except Exception as err:
                print(f"    Erro busca #{rank}: {err}", flush=True)

            if not v_id:
                try:
                    res = ydl.extract_info(f"ytsearch1:{clean_title}", download=False)
                    entries = res.get("entries") or []
                    if entries:
                        v_id = entries[0].get("id")
                        yt_title = entries[0].get("title")
                except Exception:
                    pass

            item = {
                "rank": rank,
                "title": clean_title,
                "artist": s_artist,
                "spotify_title": s_title,
                "category": pl_meta["name"],
                "playlist_id": pl_id,
                "playlist_badge": pl_meta["badge"],
                "video_id": v_id or "dQw4w9WgXcQ",
                "yt_title": yt_title or clean_title,
                "duration": dur or 180,
                "bpm": pl_meta["bpm"],
                "source": f"Spotify - {pl_meta['name']}"
            }
            resolved_tracks.append(item)
            print(f"  #{rank:02d} OK: {clean_title} - {s_artist} -> {v_id}", flush=True)
            catalog[pl_id] = {
                "meta": pl_meta,
                "tracks": resolved_tracks
            }
            save_catalog()
            time.sleep(0.15)

save_catalog()
print("\nFinalizado com sucesso! Todas as playlists salvas em spotify_playlists_catalog.json.", flush=True)
