"""
Script dedicado EXCLUSIVAMENTE para reorganizar as músicas na playlist do YouTube por categorias.

Ele lê o arquivo editável `playlist_categories.json`.
Você pode visualizar a ordem (--preview) ou aplicar a ordenação na playlist do YouTube (--apply).
Também permite alterar a categoria de uma música (--set-category).
"""

import argparse
import json
import sys
import time
from pathlib import Path
from igtoyt.youtube_auth import get_youtube_client

CATEGORIES_FILE = Path("playlist_categories.json")
CLIENT_SECRET_FILE = Path("client_secret.json")
TOKEN_FILE = Path("token.json")

# Ordem padrão em que os blocos de gênero aparecem na playlist
DEFAULT_CATEGORY_ORDER = [
    "Eletrônica",
    "Sertanejo & Forró",
    "Funk & Mega Funk",
    "Trap & Rap",
    "Reggaeton & Latino",
    "Rock & Pop",
    "Outros"
]

CATEGORY_EMOJIS = {
    "Eletrônica": "⚡",
    "Sertanejo & Forró": "🤠",
    "Funk & Mega Funk": "🔊",
    "Trap & Rap": "🎤",
    "Reggaeton & Latino": "🌴",
    "Rock & Pop": "🎸",
    "Outros": "🎧",
}


def load_catalog() -> list[dict]:
    if not CATEGORIES_FILE.exists():
        print(f"Erro: Arquivo '{CATEGORIES_FILE}' não encontrado!")
        sys.exit(1)
    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_catalog(catalog: list[dict]) -> None:
    with open(CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)


def preview_order(catalog: list[dict]) -> None:
    print("=" * 60)
    print("PREVIEW DA REORGANIZAÇÃO POR CATEGORIAS")
    print("=" * 60)

    total_valid = sum(1 for item in catalog if item.get("video_id"))
    print(f"Total de músicas com vídeo: {total_valid} de {len(catalog)}\n")

    for cat in DEFAULT_CATEGORY_ORDER:
        tracks = [t for t in catalog if t.get("category") == cat and t.get("video_id")]
        emoji = CATEGORY_EMOJIS.get(cat, "🎵")
        print(f"\n{emoji} === BLOCO: {cat.upper()} ({len(tracks)} músicas) ===")
        for i, t in enumerate(tracks, 1):
            artist = t.get("artist") or "Desconhecido"
            title = t.get("title") or "Sem título"
            print(f"  {i:2d}. {artist} - {title}")

    print("\n" + "=" * 60)
    print("Dica: Para aplicar esta ordem no YouTube, execute:")
    print("python reorganize_playlist.py --apply")
    print("=" * 60)


def set_track_category(catalog: list[dict], query: str, new_category: str) -> None:
    query_lower = query.lower()
    matches = []
    for item in catalog:
        title = (item.get("title") or "").lower()
        artist = (item.get("artist") or "").lower()
        if query_lower in title or query_lower in artist:
            matches.append(item)

    if not matches:
        print(f"Nenhuma música encontrada com o termo: '{query}'")
        return

    if len(matches) > 1:
        print(f"Foram encontradas {len(matches)} músicas. Seja mais específico:")
        for m in matches:
            print(f"  - [{m.get('category')}] {m.get('artist')} - {m.get('title')}")
        return

    item = matches[0]
    old_cat = item.get("category")
    item["category"] = new_category
    save_catalog(catalog)
    print(f"Categoria atualizada com sucesso!")
    print(f"Música: {item.get('artist')} - {item.get('title')}")
    print(f"De: [{old_cat}] -> Para: [{new_category}]")


def apply_to_youtube(catalog: list[dict], playlist_title: str = "Músicas do Instagram") -> None:
    print("\nConectando à API do YouTube...")
    try:
        yt = get_youtube_client(CLIENT_SECRET_FILE, TOKEN_FILE)
    except Exception as e:
        print(f"Erro ao autenticar com YouTube: {e}")
        return

    # Buscar playlist
    try:
        playlists_res = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    except Exception as e:
        if "quotaExceeded" in str(e):
            print("\n[!] Atenção: A cota diária gratuita da API do YouTube (10.000 unidades) foi atingida hoje.")
            print("O Google reseta essa cota automaticamente à meia-noite PST (madrugada no Brasil).")
            print("Assim que resetar, basta rodar novamente:")
            print("python reorganize_playlist.py --apply")
            return
        print(f"Erro ao consultar playlists: {e}")
        return

    target_playlist_id = None
    for p in playlists_res.get("items", []):
        if p["snippet"]["title"].strip().lower() == playlist_title.lower():
            target_playlist_id = p["id"]
            break

    if not target_playlist_id:
        print(f"Playlist '{playlist_title}' não encontrada no seu canal.")
        return

    print(f"Playlist encontrada: {playlist_title} (ID: {target_playlist_id})")

    # Mapear ordem desejada
    ordered_tracks = []
    for cat in DEFAULT_CATEGORY_ORDER:
        tracks = [t for t in catalog if t.get("category") == cat and t.get("video_id")]
        ordered_tracks.extend(tracks)

    video_to_target_pos = {t["video_id"]: idx for idx, t in enumerate(ordered_tracks)}

    # Buscar itens da playlist no YouTube
    print("Carregando itens atuais da playlist no YouTube...")
    current_items = []
    page_token = None
    try:
        while True:
            res = yt.playlistItems().list(
                part="snippet",
                playlistId=target_playlist_id,
                maxResults=50,
                pageToken=page_token
            ).execute()
            current_items.extend(res.get("items", []))
            page_token = res.get("nextPageToken")
            if not page_token:
                break
    except Exception as e:
        if "quotaExceeded" in str(e):
            print("\n[!] A cota diária da API do YouTube foi atingida hoje.")
            print("As categorias já foram 100% atualizadas no arquivo local 'playlist_categories.json'.")
            print("Rode novamente amanhã após o reset da cota com: python reorganize_playlist.py --apply")
            return
        print(f"Erro ao listar itens da playlist: {e}")
        return

    print(f"Total de vídeos atualmente na playlist: {len(current_items)}")
    print("Reordenando músicas nos blocos de categoria...")

    # Atualizar posições que não batem
    moved_count = 0
    for item in current_items:
        item_id = item["id"]
        v_id = item["snippet"]["resourceId"]["videoId"]
        curr_pos = item["snippet"]["position"]
        target_pos = video_to_target_pos.get(v_id)

        if target_pos is not None and target_pos != curr_pos:
            try:
                yt.playlistItems().update(
                    part="snippet",
                    body={
                        "id": item_id,
                        "snippet": {
                            "playlistId": target_playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": v_id},
                            "position": target_pos,
                        }
                    }
                ).execute()
                moved_count += 1
                title = item["snippet"]["title"]
                print(f"  [Posição {curr_pos} -> {target_pos}] {title[:50]}")
                time.sleep(0.3)
            except Exception as e:
                if "quotaExceeded" in str(e):
                    print("\n[!] Cota do YouTube esgotada durante o reposicionamento.")
                    print(f"Músicas movidas até a interrupção: {moved_count}")
                    return
                print(f"  Erro ao mover item {item_id}: {e}")

    print("\nReorganização finalizada com sucesso!")
    print(f"Playlist: https://www.youtube.com/playlist?list={target_playlist_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Reorganiza as músicas na playlist do YouTube por blocos de categorias."
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Exibe no terminal a lista de músicas agrupadas por categoria sem alterar o YouTube."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Aplica a ordem das categorias diretamente na playlist do YouTube."
    )
    parser.add_argument(
        "--set-category",
        nargs=2,
        metavar=("MUSICA", "CATEGORIA"),
        help="Altera a categoria de uma música específica (ex: --set-category 'Cara de Santa' 'Funk & Mega Funk')."
    )

    args = parser.parse_args()
    catalog = load_catalog()

    if args.set_category:
        track_query, new_cat = args.set_category
        set_track_category(catalog, track_query, new_cat)
    elif args.apply:
        apply_to_youtube(catalog)
    else:
        preview_order(catalog)


if __name__ == "__main__":
    main()
