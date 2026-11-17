from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from igtoyt.identify_song import identify_song, shazamio_recognize
from igtoyt.instagram_auth import get_authenticated_loader
from igtoyt.instagram_saved import iter_saved_posts
from igtoyt.processed_store import ProcessedStore
from igtoyt.youtube_auth import get_youtube_client
from igtoyt.youtube_playlist import add_video_to_playlist, ensure_playlist
from igtoyt.youtube_search import real_ytdlp_extractor, search_youtube

PLAYLIST_TITLE = "Músicas do Instagram"
DOWNLOAD_DIR = Path("data")
CLIENT_SECRET_PATH = Path("client_secret.json")
TOKEN_PATH = Path("token.json")
PROCESSED_PATH = Path("processed.json")
COOKIES_TXT_PATH = Path("cookies.txt")


@dataclass
class Report:
    added: list[str] = field(default_factory=list)
    guessed: list[str] = field(default_factory=list)
    skipped_photos: list[str] = field(default_factory=list)
    not_identified: list[str] = field(default_factory=list)
    not_found_on_youtube: list[str] = field(default_factory=list)


def run_pipeline(
    store: ProcessedStore,
    youtube,
    playlist_id: str,
    download_dir: Path,
    saved_posts,
    identify,
    search,
    add_to_playlist,
    store_path: Optional[Path] = None,
) -> Report:
    report = Report()

    for post in saved_posts:
        if store.is_post_processed(post.shortcode):
            continue

        if not post.is_video:
            print(f"  [-] Post {post.shortcode} é foto. Ignorando.")
            report.skipped_photos.append(post.shortcode)
            store.mark(post.shortcode, "skipped_photo", None)
            if store_path:
                store.save(store_path)
            continue

        match = identify(post, post.video_path)
        if match is None:
            print(f"  [x] Nenhuma música identificada para o post {post.shortcode}.")
            report.not_identified.append(post.shortcode)
            store.mark(post.shortcode, "not_identified", None)
            if store_path:
                store.save(store_path)
            continue

        # CATEGORIZAÇÃO ESTATUTÁRIA: apenas músicas verificadas (metadata ou fingerprint Shazam)
        # são enviadas para a playlist do YouTube. Textos de legenda/palpites aleatórios são filtrados.
        if match.confidence != "exact":
            print(f"  [-] Post {post.shortcode}: sem música identificada via áudio/metadados. Ignorando texto genérico.")
            report.guessed.append(post.shortcode)
            store.mark(post.shortcode, "skipped_non_music", None)
            if store_path:
                store.save(store_path)
            continue

        track_name = f"{match.title or ''} - {match.artist or ''}".strip(" -") or match.query
        print(f"  [🎵] Música confirmada ({match.method}): {track_name}")
        video = search(match.query)
        if video is None:
            print(f"  [x] Não encontrado no YouTube: {match.query}")
            report.not_found_on_youtube.append(post.shortcode)
            store.mark(post.shortcode, "not_found_on_youtube", None)
            if store_path:
                store.save(store_path)
            continue

        print(f"  [+] YouTube: {video.title} ({video.url})")
        if youtube is not None:
            added = add_to_playlist(youtube, playlist_id, video.video_id, store)
            if added:
                print(f"  [V] Adicionada com sucesso à playlist!")
            else:
                print(f"  [=] Já existe na playlist (duplicata evitada).")
        else:
            add_to_playlist(youtube, playlist_id, video.video_id, store)

        report.added.append(post.shortcode)
        store.mark(post.shortcode, "added", video.video_id)

        if store_path:
            store.save(store_path)

    return report


def main() -> None:
    loader = get_authenticated_loader(
        cookies_txt_path=COOKIES_TXT_PATH if COOKIES_TXT_PATH.exists() else None
    )
    youtube = get_youtube_client(CLIENT_SECRET_PATH, TOKEN_PATH)
    playlist_id = ensure_playlist(youtube, PLAYLIST_TITLE)
    store = ProcessedStore.load(PROCESSED_PATH)

    saved_posts = iter_saved_posts(
        loader,
        DOWNLOAD_DIR,
        cookies_txt_path=COOKIES_TXT_PATH if COOKIES_TXT_PATH.exists() else None,
    )

    def identify(post, video_path):
        return identify_song(post, video_path, shazamio_recognize)

    def search(query):
        return search_youtube(query, real_ytdlp_extractor)

    report = run_pipeline(
        store,
        youtube,
        playlist_id,
        DOWNLOAD_DIR,
        saved_posts,
        identify,
        search,
        add_video_to_playlist,
        store_path=PROCESSED_PATH,
    )
    store.save(PROCESSED_PATH)

    print("\n" + "=" * 40)
    print("RESUMO DO PROCESSAMENTO")
    print("=" * 40)
    print(f"Músicas adicionadas à playlist: {len(report.added)}")
    print(f"Vídeos/posts sem música filtrados: {len(report.guessed)}")
    print(f"Fotos ignoradas: {len(report.skipped_photos)}")
    print(f"Áudio não identificado: {len(report.not_identified)}")
    print(f"Músicas não encontradas no YouTube: {len(report.not_found_on_youtube)}")


if __name__ == "__main__":
    main()
