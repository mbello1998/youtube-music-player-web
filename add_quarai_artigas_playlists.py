import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PLAYLISTS_DEF = [
    {
        "id": "quarai_artigas_fronteira_paz",
        "name": "🧉 Fronteira da Paz: Quaraí & Artigas (Hits)",
        "icon": "🇺🇾",
        "genre": "Fronteira Quaraí & Artigas",
        "desc": "As músicas mais escutadas na fronteira de Quaraí (RS) e Artigas (Uruguai): da charanga e cumbia uruguaia ao vaneirão e nativismo da fronteira.",
        "search_queries": [
            "Miriam Britos Amor Prohibido",
            "Mano Lima O Homem do Pala Branco",
            "Chacho Ramos Que Tiene la Noche",
            "Baitaca Do Fundo da Grota",
            "Lucas Sugo Cinco Minutos",
            "Sonido Profesional Compañera Mía",
            "Joca Martins Domingueiro",
            "Matías Valdéz Latidos",
            "Os Serranos Criado em Galpão",
            "The La Planta Cariñito",
            "Tchê Barbaridade Moça Fandangueira",
            "Miriam Britos Me Vas a Pagar"
        ]
    },
    {
        "id": "artigas_charanga_cumbia",
        "name": "🇺🇾 Artigas: Charanga & Cumbia Uruguaia",
        "icon": "🎺",
        "genre": "Charanga & Cumbia de Artigas",
        "desc": "A verdadeira charanga e cumbia que toca no interior de Artigas e norte do Uruguai: Miriam Britos, Sonido Profesional, Chacho Ramos e Lucas Sugo.",
        "search_queries": [
            "Miriam Britos Corazon Barato",
            "Sonido Profesional El Borracho",
            "Chacho Ramos En un Rincon del Alma",
            "Lucas Sugo Hechicera",
            "Miriam Britos A Chillar a Otra Parte",
            "Matías Valdéz Volver a Verte",
            "Sonido Profesional Llego la Charanga",
            "Chacho Ramos La Charanga",
            "The La Planta Barco a la Deriva",
            "Miriam Britos No Me Arrepiento de Este Amor"
        ]
    },
    {
        "id": "quarai_gaucho_fronteira",
        "name": "🇧🇷 Quaraí: Vanera, Chamamé & Nativismo da Fronteira",
        "icon": "🧉",
        "genre": "Fronteira Gaúcha & Vanera",
        "desc": "O autêntico som campeiro e tradicionalista da fronteira de Quaraí (RS): Mano Lima, Baitaca, Joca Martins, Luiz Marenco e Os Serranos.",
        "search_queries": [
            "Mano Lima Baile do Sapucay",
            "Luiz Marenco Batendo Agua",
            "Baitaca Historia do Tico Louco",
            "Joca Martins Eu Sou Bagual",
            "Grupo Rodeio Iguaria Campeira",
            "Os Serranos O Vento",
            "Mano Lima Amigo do Peito",
            "Cesar Oliveira Rogerio Melo Paleteada",
            "Tche Garotos Menininha Meu Amor",
            "Luiz Marenco Pra Onde Vai Meu Rio"
        ]
    }
]

import yt_dlp

def search_yt_track(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': True,
        'default_search': 'ytsearch1'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch1:{query}", download=False)
            if not res or 'entries' not in res or len(res['entries']) == 0:
                return query, None
            data = res['entries'][0]
            vid = data.get("id")
            title = data.get("title", query)
            channel = data.get("channel") or data.get("uploader") or "Fronteira Quaraí & Artigas"
            duration = data.get("duration") or 210
            
            mins = int(duration // 60)
            secs = int(duration % 60)
            dur_str = f"{mins}:{secs:02d}"

            q_low = query.lower()
            if any(w in q_low for w in ["vanera", "fandango", "sapucay", "grota", "louco", "bagual", "serranos"]):
                bpm = 138
            elif any(w in q_low for w in ["milonga", "marenco", "batendo"]):
                bpm = 92
            elif any(w in q_low for w in ["charanga", "miriam britos", "sonido profesional", "chacho ramos"]):
                bpm = 98
            elif any(w in q_low for w in ["lucas sugo", "matias valdez", "planta"]):
                bpm = 100
            else:
                bpm = 110

            return query, {
                "video_id": vid,
                "title": title,
                "artist": channel,
                "bpm": bpm,
                "duration": dur_str,
                "source": "YouTube (Oficial Fronteira)"
            }
    except Exception as e:
        print(f"Erro em {query}: {e}")
        return query, None

def main():
    catalog_path = Path("spotify_playlists_catalog.json")
    if not catalog_path.exists():
        print("spotify_playlists_catalog.json not found!")
        return

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    all_queries = []
    for pl in PLAYLISTS_DEF:
        for q in pl["search_queries"]:
            all_queries.append(q)

    print(f"Resolvendo {len(all_queries)} faixas de Quaraí & Artigas em paralelo...")
    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        for q, res in executor.map(search_yt_track, all_queries):
            if res and res.get("video_id"):
                results[q] = res
                print(f"✓ [{res['bpm']} BPM] {res['title']} -> {res['video_id']}")
            else:
                print(f"✗ Falha ao resolver: {q}")

    # Build playlists in catalog
    added_count = 0
    for pl_def in PLAYLISTS_DEF:
        pl_id = pl_def["id"]
        tracks = []
        for q in pl_def["search_queries"]:
            if q in results:
                tracks.append(results[q])

        catalog[pl_id] = {
            "meta": {
                "name": pl_def["name"],
                "icon": pl_def["icon"],
                "genre": pl_def["genre"],
                "desc": pl_def["desc"]
            },
            "tracks": tracks
        }
        added_count += 1
        print(f"Playlist adicionada: {pl_def['name']} com {len(tracks)} faixas.")

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\nSucesso: Catálogo atualizado com {len(catalog)} playlists (+{added_count} de Quaraí & Artigas).")

if __name__ == "__main__":
    main()
