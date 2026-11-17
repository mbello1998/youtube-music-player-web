"""
Script para sincronizar todas as músicas selecionadas na fila (pending_queue.json)
diretamente com a sua playlist 'Músicas do Instagram' no YouTube.
"""

import json
import time
from pathlib import Path
from igtoyt.youtube_auth import get_youtube_client

QUEUE_FILE = Path("pending_queue.json")
CLIENT_SECRET_FILE = Path("client_secret.json")
TOKEN_FILE = Path("token.json")
PLAYLIST_TITLE = "Músicas do Instagram"


def sync_queue():
    if not QUEUE_FILE.exists():
        print("Nenhuma fila encontrada em pending_queue.json.")
        return

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        queue = json.load(f)

    if not queue:
        print("A fila está vazia. Adicione músicas pelo player em http://localhost:5500!")
        return

    print(f"Total de músicas na fila para enviar ao YouTube: {len(queue)}")
    
    try:
        yt = get_youtube_client(CLIENT_SECRET_FILE, TOKEN_FILE)
    except Exception as e:
        print(f"Erro ao autenticar com o YouTube: {e}")
        return

    # Buscar playlist
    try:
        playlists_res = yt.playlists().list(part="snippet", mine=True, maxResults=50).execute()
    except Exception as e:
        if "quotaExceeded" in str(e):
            print("\n[!] A cota diária do YouTube ainda está atingida. Ela renova automaticamente à meia-noite PST.")
            print(f"Sua fila com {len(queue)} músicas continua 100% salva e segura no arquivo pending_queue.json!")
            return
        print(f"Erro ao buscar playlist: {e}")
        return

    playlist_id = None
    for p in playlists_res.get("items", []):
        if p["snippet"]["title"].strip().lower() == PLAYLIST_TITLE.lower():
            playlist_id = p["id"]
            break

    if not playlist_id:
        print(f"Playlist '{PLAYLIST_TITLE}' não encontrada no seu canal.")
        return

    print(f"Conectado à playlist '{PLAYLIST_TITLE}' ({playlist_id})!")
    
    added_count = 0
    remaining_queue = []

    for i, track in enumerate(queue, 1):
        v_id = track.get("video_id")
        title = track.get("title")
        artist = track.get("artist", "")
        
        try:
            yt.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": playlist_id,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": v_id,
                        }
                    }
                }
            ).execute()
            added_count += 1
            print(f"  [{i}/{len(queue)}] [+] Adicionada ao YouTube: {artist} - {title}")
            time.sleep(0.3)
        except Exception as e:
            if "quotaExceeded" in str(e):
                print(f"\n[!] Cota do YouTube esgotada na música {i}. {added_count} músicas adicionadas hoje.")
                remaining_queue.extend(queue[i-1:])
                break
            else:
                print(f"  [x] Erro ao adicionar {title}: {e}")

    # Salva apenas o que restou (se tudo foi adicionado, zera a fila)
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(remaining_queue, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print(f"Sincronização concluída! {added_count} músicas adicionadas à playlist.")
    if remaining_queue:
        print(f"{len(remaining_queue)} músicas continuam salvas na fila para a próxima renovação de cota.")
    else:
        print("Toda a sua fila foi inserida na playlist com sucesso!")
    print(f"Acesse: https://www.youtube.com/playlist?list={playlist_id}")


if __name__ == "__main__":
    sync_queue()
