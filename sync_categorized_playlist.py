import json
import time
from pathlib import Path
from igtoyt.youtube_auth import get_youtube_client

CATEGORY_ORDER = [
    "Eletrônica",
    "Sertanejo & Forró",
    "Funk & Mega Funk",
    "Trap & Rap",
    "Reggaeton & Latino",
    "Rock & Pop",
    "Outros",
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


def main():
    resolved_path = Path("audio_catalog_resolved.json")
    if not resolved_path.exists():
        print("Erro: audio_catalog_resolved.json não encontrado!")
        return

    with open(resolved_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # Filtrar apenas as músicas com video_id encontrado
    valid_tracks = [t for t in catalog.values() if t.get("video_id")]
    print(f"Total de faixas válidas para adicionar: {len(valid_tracks)}")

    # Ordenar por categoria na ordem definida
    def sort_key(track):
        cat = track.get("category", "Outros")
        idx = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else len(CATEGORY_ORDER)
        return (idx, track.get("title", "").lower())

    sorted_tracks = sorted(valid_tracks, key=sort_key)

    # Autenticar no YouTube
    yt = get_youtube_client(Path("client_secret.json"), Path("token.json"))

    # Buscar playlist existente "Músicas do Instagram" para recriar de forma 100% limpa e categorizada
    old_playlists = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    existing_id = None
    for item in old_playlists.get("items", []):
        if item["snippet"]["title"].strip().lower() == "músicas do instagram":
            existing_id = item["id"]
            break

    if existing_id:
        print(f"Removendo playlist antiga não categorizada ({existing_id}) para recriar perfeitamente ordenada...")
        try:
            yt.playlists().delete(id=existing_id).execute()
            print("Playlist antiga removida com sucesso!")
        except Exception as e:
            print(f"Aviso ao remover playlist antiga: {e}")

    # Criar nova playlist limpa e organizada
    desc = (
        "Músicas salvas do Instagram (@matheus.b.p) organizadas por blocos de categoria: "
        "Eletrônica, Sertanejo & Forró, Funk & Mega Funk, Trap & Rap, Reggaeton & Latino, Rock & Pop."
    )
    print("Criando nova playlist 'Músicas do Instagram' no YouTube...")
    new_pl = (
        yt.playlists()
        .insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": "Músicas do Instagram",
                    "description": desc,
                },
                "status": {"privacyStatus": "public"},
            },
        )
        .execute()
    )
    playlist_id = new_pl["id"]
    playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"
    print(f"Playlist criada com sucesso: {playlist_url}")

    progress_path = Path("processed_categorized.json")
    progress = {}
    if progress_path.exists():
        try:
            with open(progress_path, "r", encoding="utf-8") as f:
                progress = json.load(f)
        except Exception:
            progress = {}

    current_category = None
    added_count = 0

    print("\nIniciando inserção das músicas organizadas por categoria:")
    for i, track in enumerate(sorted_tracks, 1):
        cat = track.get("category", "Outros")
        if cat != current_category:
            current_category = cat
            emoji = CATEGORY_EMOJIS.get(cat, "🎵")
            cat_tracks = [t for t in sorted_tracks if t.get("category") == cat]
            print(f"\n{emoji} === BLOCO: {cat.upper()} ({len(cat_tracks)} músicas) ===")

        audio_id = track["id"]
        video_id = track["video_id"]
        title = track.get("title")
        artist = track.get("artist")

        # Inserção com retry
        success = False
        for attempt in range(3):
            try:
                yt.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id,
                            },
                        }
                    },
                ).execute()
                success = True
                break
            except Exception as e:
                if "409" in str(e) or "503" in str(e):
                    time.sleep(2)
                    continue
                print(f"  [x] Erro ao adicionar {title}: {e}")
                break

        if success:
            added_count += 1
            progress[audio_id] = {
                "status": "added",
                "video_id": video_id,
                "category": cat,
                "title": title,
                "artist": artist,
            }
            print(f"  [{i:3d}/{len(sorted_tracks)}] [+] {artist} - {title}")
        else:
            progress[audio_id] = {"status": "error", "video_id": video_id}

        if i % 10 == 0:
            with open(progress_path, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)

        # Pequeno delay para respeitar rate-limit da API do YouTube
        time.sleep(0.3)

    with open(progress_path, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print("SINCRONIZAÇÃO E ORGANIZAÇÃO CONCLUÍDAS COM SUCESSO!")
    print("=" * 50)
    print(f"Total de músicas adicionadas: {added_count}/{len(sorted_tracks)}")
    print(f"Acesse sua playlist organizada aqui: {playlist_url}")


if __name__ == "__main__":
    main()
