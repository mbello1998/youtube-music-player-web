# -*- coding: utf-8 -*-
"""
add_fiestero_cumbia_playlists.py
Cria playlists autênticas de Mix Fiesteros e Enganchados Cumbia Fiestera Remix
e sincroniza as faixas com spotify_playlists_catalog.json e complete_library.json.
"""

import json
from pathlib import Path

SPOTIFY_CATALOG_FILE = Path("spotify_playlists_catalog.json")
LIBRARY_FILE = Path("complete_library.json")

FIRESTERO_PLAYLISTS = [
    {
        "id": "mix_fiesteros_previa_boliche_2026",
        "name": "Mix Fiesteros & Previa Boliche 2026",
        "badge": "🎉 Mix Fiesteros",
        "icon": "🔥",
        "genre": "Cumbia Fiestera & Cachengue",
        "desc": "Os melhores sets de festa, previa de boliche e cachengue fiestero para manter a pista no ápice da energia!",
        "bpm": 128,
        "tracks": [
            {
                "title": "MIX FIESTERO #11 😎 | PREVIA Y CACHENGUE 2026 | CHEKO DJ | LO MAS ESCUCHADO Y NUEVO AGOSTO 🔥",
                "artist": "CHEKO DJ",
                "video_id": "4ugmfIPxOCw",
                "duration": 1820,
                "bpm": 128
            },
            {
                "title": "MIX FIESTERO 2026 🔥 [Parte 1] PREVIA Y CACHENGUE | LO MAS ESCUCHADO - DJ Cu3rvo",
                "artist": "DJ Cu3rvo",
                "video_id": "Jt-_OWyUeL8",
                "duration": 1540,
                "bpm": 126
            },
            {
                "title": "🌼MIX FIESTERO 2026🥳 LO MAS ESCUCHADO | ENGANCHADO CACHENGUE | NOVIEMBRE | LukkasRmx",
                "artist": "LukkasRmx",
                "video_id": "LlrIoYY77Vw",
                "duration": 1420,
                "bpm": 127
            },
            {
                "title": "El Reja, Herederos Para Vos - Mix Fiestero (Baila Sola/La Gata) | Video Oficial",
                "artist": "El Reja",
                "video_id": "nSR86YmPzg0",
                "duration": 210,
                "bpm": 130
            },
            {
                "title": "MIX FIESTERO Vol 10 ( Enganchado 2023) - DJ X",
                "artist": "DJ X",
                "video_id": "ELgHgmchY2k",
                "duration": 1650,
                "bpm": 123
            },
            {
                "title": "MIX FIESTERO 2026 🌴💣 - DJ Favio Alabart Ft @DJVaneperez",
                "artist": "DJ Favio Alabart",
                "video_id": "UzUuEaOWMbg",
                "duration": 1780,
                "bpm": 128
            },
            {
                "title": "MIX FIESTERO #6 😈 LO MAS NUEVO 2024 - CHEKO DJ - DICIEMBRE 2024",
                "artist": "CHEKO DJ",
                "video_id": "E6_el7jdaA0",
                "duration": 1600,
                "bpm": 126
            },
            {
                "title": "MIX BOLICHE DISCOTECA - REGGAETON, PERREO FUNK , DEMBOW , TECH HOUSE",
                "artist": "DJ Boliche",
                "video_id": "cqiOJVRDt-g",
                "duration": 1950,
                "bpm": 128
            }
        ]
    },
    {
        "id": "enganchados_cumbia_fiestera_remix",
        "name": "•ENGANCHADO CUMBIA FIESTERA REMIX•",
        "badge": "🎺 Enganchados Fiesteros",
        "icon": "😈",
        "genre": "Cumbia Del Recuerdo & Retro Fiestera",
        "desc": "O lendário Enganchado Cumbia Fiestera Remix: Cumbias Inolvidables, Cumbia Del Recuerdo e Retro para cantar junto e pular!",
        "bpm": 124,
        "tracks": [
            {
                "title": "•ENGANCHADO CUMBIA FIESTERA REMIX•😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro 🐼",
                "artist": "Cumbias Inolvidables",
                "video_id": "PFShMpSiiYQ",
                "duration": 2400,
                "bpm": 124
            },
            {
                "title": "•ENGANCHADO CUMBIA FIESTERA REMIX Vol 2•😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro",
                "artist": "Cumbias Inolvidables",
                "video_id": "gVL1WNb76EA",
                "duration": 2280,
                "bpm": 125
            },
            {
                "title": "•ENGANCHADO CUMBIA FIESTERA REMIX Vol 3•😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro",
                "artist": "Cumbias Inolvidables",
                "video_id": "pJXLbaIzlUI",
                "duration": 2150,
                "bpm": 123
            },
            {
                "title": "•ENGANCHADO CUMBIA FIESTERA REMIX Especial•😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo",
                "artist": "Cumbias Inolvidables",
                "video_id": "sLIkJAH5hA0",
                "duration": 2350,
                "bpm": 124
            },
            {
                "title": "•ENGANCHADO CUMBIA FIESTERA 2023 REMIX•😈 [ Cumbias Inolvidables ] Cumbia Del Recuerdo - Cumbia Retro",
                "artist": "Cumbias Inolvidables",
                "video_id": "wIg1XlEsJ8g",
                "duration": 2100,
                "bpm": 125
            },
            {
                "title": "RETRO CACHENGUE Vol.1 - LATINOS FIESTEROS ✘ Dj Sergio Altamirano",
                "artist": "Dj Sergio Altamirano",
                "video_id": "XNG2R6pqgK0",
                "duration": 1820,
                "bpm": 122
            }
        ]
    },
    {
        "id": "cumbia_fiestera_sonido_profesional",
        "name": "Sonido Profesional & Latinos Fiesteros",
        "badge": "🇺🇾 Latinos Fiesteros",
        "icon": "🍻",
        "genre": "Charanga & Cumbia Fiestera",
        "desc": "Os sucessos mais cantados de Sonido Profesional e enganchados clássicos de fronteira e boliche!",
        "bpm": 122,
        "tracks": [
            {
                "title": "Nadie Me Vera Llorar - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "u06kE4fX1oE",
                "duration": 210,
                "bpm": 122
            },
            {
                "title": "Por Ultima Vez - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "ebWugNuY5wU",
                "duration": 205,
                "bpm": 126
            },
            {
                "title": "Besos En Guerra - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "N-L1b41p24I",
                "duration": 198,
                "bpm": 122
            },
            {
                "title": "Diablo - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "mXl9iK6uMzA",
                "duration": 215,
                "bpm": 120
            },
            {
                "title": "AX-13 ft SONIDO PROFESIONAL - TAN CASUAL",
                "artist": "Sonido Profesional",
                "video_id": "qH1jK28xK7w",
                "duration": 212,
                "bpm": 119
            },
            {
                "title": "Como Antes - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "fYUrzOV9mNQ",
                "duration": 218,
                "bpm": 124
            },
            {
                "title": "Si Supieras - Sonido Profesional",
                "artist": "Sonido Profesional",
                "video_id": "hYdkzCJLvow",
                "duration": 204,
                "bpm": 122
            }
        ]
    }
]

def update_catalog():
    if not SPOTIFY_CATALOG_FILE.exists():
        print(f"{SPOTIFY_CATALOG_FILE} não existe!")
        return
    with open(SPOTIFY_CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    for p in FIRESTERO_PLAYLISTS:
        pid = p["id"]
        meta = {
            "id": pid,
            "name": p["name"],
            "badge": p["badge"],
            "icon": p["icon"],
            "genre": p["genre"],
            "desc": p["desc"],
            "bpm": p["bpm"]
        }
        tracks = []
        for i, t in enumerate(p["tracks"]):
            tracks.append({
                "rank": i + 1,
                "title": t["title"],
                "artist": t["artist"],
                "category": "Reggaeton, Cachengue & Latino",
                "playlist_id": pid,
                "playlist_badge": p["badge"],
                "video_id": t["video_id"],
                "duration": t["duration"],
                "bpm": t["bpm"],
                "source": f"Spotify - {p['name']}"
            })
        catalog[pid] = {
            "meta": meta,
            "tracks": tracks
        }
        print(f"Playlist adicionada ao catálogo: {p['name']} ({len(tracks)} faixas)")

    with open(SPOTIFY_CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Catálogo salvo: total de {len(catalog)} playlists!")

def update_library():
    if not LIBRARY_FILE.exists():
        print(f"{LIBRARY_FILE} não existe!")
        return
    with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
        library = json.load(f)

    existing_ids = {t.get("video_id") for t in library if t.get("video_id")}
    added = 0
    for p in FIRESTERO_PLAYLISTS:
        for t in p["tracks"]:
            vid = t["video_id"]
            if vid and vid not in existing_ids:
                library.append({
                    "title": t["title"],
                    "artist": t["artist"],
                    "video_id": vid,
                    "duration": t["duration"],
                    "bpm": t["bpm"],
                    "category": "Reggaeton, Cachengue & Latino",
                    "source": f"Mix Fiestero ({p['badge']})"
                })
                existing_ids.add(vid)
                added += 1

    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(library, f, indent=2, ensure_ascii=False)
    print(f"Biblioteca atualizada: {added} novas faixas adicionadas em 'Reggaeton, Cachengue & Latino'! Total: {len(library)}")

if __name__ == "__main__":
    update_catalog()
    update_library()
