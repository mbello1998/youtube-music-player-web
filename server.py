import http.server
import json
import re
from pathlib import Path
import socketserver
import sys
import threading
import time
import urllib.parse
import urllib.request
import yt_dlp

PORT = 5050
QUEUE_FILE = Path("pending_queue.json")
SUGGESTIONS_FILE = Path("suggested_tracks.json")
SEEN_FILE = Path("seen_suggested_ids.json")
ROTATION_FILE = Path("genre_rotation.json")
LIBRARY_FILE = Path("complete_library.json")
HISTORY_FILE = Path("playback_history.json")

AUDIO_CACHE = {}
AUDIO_CACHE_TTL = 3600  # 1 hora para evitar expiração de token do YouTube

def get_audio_info(video_id, force_refresh=False):
    if not video_id:
        return None
    cached = AUDIO_CACHE.get(video_id)
    if not force_refresh and cached and (time.time() - cached.get("time", 0)) < AUDIO_CACHE_TTL:
        return cached
    try:
        ydl_opts = {
            "format": "bestaudio[ext=m4a]/bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
            "socket_timeout": 10,
        }
        if Path("cookies.txt").exists() and Path("cookies.txt").stat().st_size > 0:
            ydl_opts["cookiefile"] = "cookies.txt"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info.get("url")
            http_headers = info.get("http_headers") or {}
            if not url:
                formats = info.get("formats", [])
                audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
                if audio_formats:
                    m4a_fmts = [f for f in audio_formats if f.get("ext") == "m4a"]
                    chosen = m4a_fmts[-1] if m4a_fmts else audio_formats[-1]
                    url = chosen.get("url")
                    if chosen.get("http_headers"):
                        http_headers.update(chosen["http_headers"])
                elif formats:
                    chosen = formats[-1]
                    url = chosen.get("url")
                    if chosen.get("http_headers"):
                        http_headers.update(chosen["http_headers"])
            
            duration = info.get("duration") or 0
            ext = info.get("ext") or "m4a"
            res = {
                "url": url,
                "duration": duration,
                "ext": ext,
                "http_headers": http_headers,
                "time": time.time()
            }
            if url:
                AUDIO_CACHE[video_id] = res
            return res
    except Exception as e:
        err_str = str(e)
        if "Video unavailable" in err_str or "This video is not available" in err_str or "Private video" in err_str:
            print(f"[Aviso] Vídeo indisponível ou excluído no YouTube ({video_id}).")
        else:
            print(f"Erro ao extrair áudio de {video_id}: {e}")
        return None

def get_direct_audio_url(video_id):
    info = get_audio_info(video_id)
    return info["url"] if info else None

def prewarm_audio_cache(video_ids):
    def _worker():
        for vid in video_ids:
            if vid and vid not in AUDIO_CACHE:
                try:
                    get_audio_info(vid)
                except Exception:
                    pass
    threading.Thread(target=_worker, daemon=True).start()


GENRE_BPM_RANGES = {
    "Mega Funk & Ritmadas": (130, 150, 138),
    "Funk Paulista, BH & Mandelão": (128, 140, 130),
    "Eletrônica, House & Desande": (124, 128, 126),
    "Sertanejo Universitário & Atual": (110, 130, 118),
    "Sertanejo Antigo & Modão": (80, 110, 95),
    "Reggaeton, Cachengue & Latino": (90, 105, 96),
    "Samba & Pagode": (90, 115, 102),
    "Trap & Rap Nacional": (120, 145, 135),
    "Rock & Pop Nostalgia": (110, 135, 122),
    "Outros": (115, 130, 124)
}

def detect_or_estimate_bpm(title: str, category: str = "Outros") -> int:
    import re, hashlib
    if not title:
        return 120
    # 1. Procurar BPM explícito no título: ex. "135 BPM", "130bpm", "140 bpm"
    m = re.search(r'\b(1[0-9]{2}|[7-9][0-9])\s*bpm\b', title, re.IGNORECASE)
    if m:
        try:
            val = int(m.group(1))
            if 60 <= val <= 200:
                return val
        except Exception:
            pass
    # 2. Estimativa realista baseada no gênero musical com hash determinístico
    low, high, default = GENRE_BPM_RANGES.get(category, (115, 130, 124))
    offset = int(hashlib.md5(title.encode('utf-8', errors='ignore')).hexdigest(), 16) % (high - low + 1)
    return low + offset


GENRE_SEARCH_QUERIES = {
    "Mega Funk & Ritmadas": [
        "Mega Funk 2024 lancamento",
        "Ritmada DJ Graeff",
        "Mega Funk eletrofunk SC",
        "Mega Funk Sanchezz DJ",
        "Mega Funk automotivo som pesado",
        "Ritmada proibidona novidades",
        "Mega Funk dancante balada",
        "Mega Funk remix 2024 hits",
        "Eletrofunk SC Floripa",
        "Ritmada montagem funk"
    ],
    "Funk Paulista, BH & Mandelão": [
        "Funk BH 2024 lancamento",
        "Mandelao SP novidades",
        "Funk ritmado BH",
        "MC Luuky MC Meno K novidades",
        "Funk consciente SP 2024",
        "Mega funk mandelao",
        "Funk paulista pesado",
        "Funk de rua sp novidades",
        "Set de funk bh 2024"
    ],
    "Eletrônica, House & Desande": [
        "Tech House Brasil 2024",
        "Desande brasileiro novidades",
        "Brazilian Bass Vintage Culture Alok",
        "House music remix balada",
        "Nu disco house Brasil",
        "Deep house eletronica festa",
        "Eletronica festival Brasil",
        "Melodic techno Brasil 2024",
        "Slap house remix hits"
    ],
    "Sertanejo Universitário & Atual": [
        "Sertanejo universitario 2024 lancamento",
        "Henrique e Juliano novidades sertanejo",
        "Hugo e Guilherme novidades",
        "Sertanejo atual modao acustico",
        "Sertanejo balada festa 2024",
        "Zé Neto e Cristiano novidades",
        "Jorge e Mateus novidades",
        "Luan Santana hits sertanejo 2024"
    ],
    "Sertanejo Antigo & Modão": [
        "Modao sertanejo classico raiz",
        "Tiao Carreiro e Pardinho modao",
        "Milionario e Jose Rico modao bruto",
        "Chitãozinho e Xororó classicos",
        "Sertanejo raiz moda de viola",
        "Trio Parada Dura modao",
        "Geziel e Gabriel modao",
        "Modao bruto de fazenda"
    ],
    "Reggaeton, Cachengue & Latino": [
        "Reggaeton 2024 novidades latino",
        "Cachengue remix fiesta latina",
        "Bad Bunny Feid reggaeton hits",
        "Urbano latino perreo remix",
        "Plan B Wisin Yandel reggaeton classico",
        "Reggaeton bailable fiesta",
        "Cumbia cachengue argentina remix",
        "Dembow latino 2024"
    ],
    "Samba & Pagode": [
        "Pagode 2024 lancamento novidades",
        "Pagode Menos e Mais churrasco",
        "Ferrugem Dilsinho pagode atual",
        "Samba de raiz roda de samba",
        "Turma do Pagode novidades",
        "Grupo Revelacao Sorriso Maroto",
        "Pagode ao vivo churrasco balada",
        "Thiaguinho pagode hits"
    ],
    "Trap & Rap Nacional": [
        "Trap nacional 2024 lancamento",
        "Matue Teto WIU novidades trap",
        "KayBlack Veigh trap novidades",
        "Rap nacional underground",
        "Trap funk ritmado",
        "Filipe Ret L7NNON trap",
        "Cabelinho trap novidades",
        "Trap beat pesado Brasil"
    ],
    "Rock & Pop Nostalgia": [
        "Pop 2000 nostalgia hits",
        "Rock nacional anos 2000",
        "Charlie Brown Jr CPM 22 classicos",
        "Pop rock internacional flashback",
        "Indie pop rock nostalgia",
        "Nacional anos 90 e 2000",
        "Rock pop 2000 flashback hits"
    ],
    "Outros": [
        "Top musicas mais tocadas Brasil 2024",
        "Hits virais do momento Brasil",
        "Remix dancante novidades 2024",
        "Músicas em alta Brasil",
        "Supermix novidades musicais"
    ]
}


_QUEUE_CACHE = {"mtime": 0.0, "data": []}

def load_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        return []
    try:
        mtime = QUEUE_FILE.stat().st_mtime
        if mtime == _QUEUE_CACHE["mtime"] and _QUEUE_CACHE["data"]:
            return _QUEUE_CACHE["data"]
        with open(QUEUE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            _QUEUE_CACHE["mtime"] = mtime
            _QUEUE_CACHE["data"] = data
            return data
    except Exception:
        return _QUEUE_CACHE["data"]


def save_queue(queue: list[dict]) -> None:
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
    try:
        _QUEUE_CACHE["mtime"] = QUEUE_FILE.stat().st_mtime
        _QUEUE_CACHE["data"] = queue
    except Exception:
        pass


def load_seen_ids() -> set[str]:
    if not SEEN_FILE.exists():
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data) if isinstance(data, list) else set()
    except Exception:
        return set()


def save_seen_ids(seen: set[str]) -> None:
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False, indent=2)


def get_next_query(category: str) -> str:
    queries = GENRE_SEARCH_QUERIES.get(category) or GENRE_SEARCH_QUERIES["Outros"]
    rotation = {}
    if ROTATION_FILE.exists():
        try:
            with open(ROTATION_FILE, "r", encoding="utf-8") as f:
                rotation = json.load(f)
        except Exception:
            pass
    curr_idx = rotation.get(category, 0)
    query = queries[curr_idx % len(queries)]
    rotation[category] = curr_idx + 1
    try:
        with open(ROTATION_FILE, "w", encoding="utf-8") as f:
            json.dump(rotation, f)
    except Exception:
        pass
    return query


def discover_tracks(category: str, custom_query: str = None, seed_bpm: int = None, limit: int = 12) -> list[dict]:
    """Busca novas músicas no YouTube para o gênero, garantindo ZERO repetição."""
    excluded_ids = set()

    # Exclusão de duplicatas apenas para descobertas/sugestões automáticas (não na pesquisa do usuário)
    if not custom_query:
        # 1. Biblioteca completa do usuário (725 faixas)
        if LIBRARY_FILE.exists():
            try:
                with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                    lib = json.load(f)
                    excluded_ids.update(t.get("video_id") for t in lib if t.get("video_id"))
            except Exception:
                pass

        # 2. Músicas já adicionadas à fila
        queue = load_queue()
        excluded_ids.update(t.get("video_id") for t in queue if t.get("video_id"))

        # 3. Músicas já sugeridas anteriormente (histórico de vistos)
        seen_ids = load_seen_ids()
        excluded_ids.update(seen_ids)

    query = custom_query if custom_query else get_next_query(category)

    results = []
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch25:{query}", download=False)
            for e in res.get("entries") or []:
                v_id = e.get("id")
                t_title = e.get("title")
                uploader = e.get("uploader") or e.get("channel") or ""
                dur = e.get("duration") or 0

                if not v_id or not t_title:
                    continue
                # Filtra shorts muito curtos ou sets gigantescos de 3 horas
                if dur > 0 and (dur < 40 or dur > 2400):
                    continue
                # Ignora faixas já existentes na biblioteca, fila ou sugestões anteriores
                if v_id in excluded_ids:
                    continue
                if any(r["video_id"] == v_id for r in results):
                    continue

                track_bpm = detect_or_estimate_bpm(t_title, category)
                results.append({
                    "video_id": v_id,
                    "title": t_title,
                    "artist": uploader,
                    "category": category,
                    "duration": dur,
                    "bpm": track_bpm,
                    "query_used": query
                })

                if len(results) >= limit:
                    break
    except Exception as ex:
        print(f"Erro ao buscar no YouTube ({category}): {ex}")

    # Registra novos IDs como vistos apenas para descobertas automáticas de gênero
    if not custom_query:
        new_ids = {r["video_id"] for r in results}
        seen_ids = load_seen_ids()
        seen_ids.update(new_ids)
        save_seen_ids(seen_ids)

    # Ordena pelo encaixe harmônico mais próximo ao BPM da música atual (para transição perfeita)
    target_bpm = seed_bpm if seed_bpm else GENRE_BPM_RANGES.get(category, (115, 130, 124))[2]
    results.sort(key=lambda x: abs(x.get("bpm", 130) - target_bpm))

    return results


def discover_related_tracks(title: str, artist: str, category: str, current_video_id: str = None, target_bpm: int = None, limit: int = 12) -> list[dict]:
    """Busca músicas semelhantes à música que está tocando agora (Spotify AI Rádio com BPM e Ritmo)."""
    import re
    clean_title = re.sub(r'\(.*?\)|\[.*?\]|feat\..*|ft\..*|clipe oficial|vídeo oficial|official video|lyric video', '', title, flags=re.IGNORECASE).strip()
    clean_artist = re.sub(r'\(.*?\)|\[.*?\]', '', artist).strip()

    excluded_ids = set()
    if current_video_id:
        excluded_ids.add(current_video_id)
    if LIBRARY_FILE.exists():
        try:
            with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                lib = json.load(f)
                excluded_ids.update(t.get("video_id") for t in lib if t.get("video_id"))
        except Exception:
            pass

    queue = load_queue()
    excluded_ids.update(t.get("video_id") for t in queue if t.get("video_id"))

    seen_ids = load_seen_ids()
    excluded_ids.update(seen_ids)

    # BPM alvo para busca acústica sincronizada
    seed_bpm = target_bpm or detect_or_estimate_bpm(clean_title or title, category)

    # Palavras do título atual para filtrar e NUNCA trazer versões da mesma música
    stop_words = {"de", "da", "do", "das", "dos", "e", "em", "um", "uma", "a", "o", "as", "os", "ao", "na", "no", "com", "por", "para", "remix", "feat", "ft", "mc", "dj", "official", "video", "clipe"}
    raw_words = re.findall(r'[a-zA-Z0-9áéíóúâêîôûãõçÁÉÍÓÚÂÊÎÔÛÃÕÇ]{3,}', clean_title.lower())
    title_keywords = [w for w in raw_words if w not in stop_words]

    # Queries no estilo Spotify AI Recommendation (Mesmo ritmo, gênero e BPM sincronizado)
    # Com referências profissionais de Treino / Academia / Motivação / Cardio
    is_high_energy = seed_bpm >= 125 or any(c in category.lower() for c in ["mega", "funk", "eletr", "desande", "trap", "ritm", "treino"])
    
    queries = []
    if is_high_energy:
        queries.extend([
            f"{category} treino pesado motivacao {seed_bpm} bpm",
            f"musica para treino academia pump {seed_bpm} bpm",
            f"cardio {seed_bpm} bpm bass boost treino",
            f"set treino musculacao {category} {seed_bpm} bpm som pesado",
            f"{category} {seed_bpm} bpm lancamento"
        ])
    else:
        queries.extend([
            f"{category} {seed_bpm} bpm lancamento",
            f"ritmo {category} {seed_bpm} bpm",
            f"set {category} {seed_bpm} bpm",
            f"novidades {category} {seed_bpm} bpm hits 2024"
        ])

    genre_list = GENRE_SEARCH_QUERIES.get(category, [])
    import random
    if genre_list:
        sample_queries = random.sample(genre_list, min(2, len(genre_list)))
        queries.extend(sample_queries)

    if clean_artist:
        if is_high_energy:
            queries.insert(0, f"{clean_artist} treino motivacao ritmo {seed_bpm} bpm")
            queries.append(f"artistas parecidos com {clean_artist} {seed_bpm} bpm treino")
        else:
            queries.insert(0, f"artistas parecidos com {clean_artist} {seed_bpm} bpm")
            queries.append(f"{clean_artist} ritmo {category} {seed_bpm} bpm")

    results = []
    ydl_opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
    }

    for q in queries:
        if len(results) >= limit:
            break
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(f"ytsearch15:{q}", download=False)
                for e in res.get("entries") or []:
                    v_id = e.get("id")
                    t_title = e.get("title")
                    uploader = e.get("uploader") or e.get("channel") or ""
                    dur = e.get("duration") or 0

                    if not v_id or not t_title:
                        continue
                    if dur > 0 and (dur < 40 or dur > 2400):
                        continue
                    if v_id in excluded_ids:
                        continue
                    if any(r["video_id"] == v_id for r in results):
                        continue

                    # FILTRO DE CONTEÚDO: Descarta se tiver o mesmo nome da música atual
                    lower_result_title = t_title.lower()
                    if title_keywords and any(kw in lower_result_title for kw in title_keywords[:2]):
                        continue

                    track_bpm = detect_or_estimate_bpm(t_title, category)
                    results.append({
                        "video_id": v_id,
                        "title": t_title,
                        "artist": uploader,
                        "category": category or "Relacionadas",
                        "duration": dur,
                        "bpm": track_bpm,
                        "source": f"Spotify AI • {track_bpm} BPM"
                    })
                    if len(results) >= limit:
                        break
        except Exception as ex:
            print(f"Erro em discover_related_tracks ({q}): {ex}")

    new_ids = {r["video_id"] for r in results}
    seen_ids.update(new_ids)
    save_seen_ids(seen_ids)

    # Ordena pelo encaixe harmônico mais próximo ao BPM da música atual (para transição perfeita)
    target_bpm = seed_bpm if seed_bpm else GENRE_BPM_RANGES.get(category, (115, 130, 124))[2]
    results.sort(key=lambda x: abs(x.get("bpm", 130) - target_bpm))

    return results



OFFICIAL_CATEGORIES = [
    "Mega Funk & Ritmadas",
    "Funk Paulista, BH & Mandelão",
    "Eletrônica, House & Desande",
    "Sertanejo Universitário & Atual",
    "Sertanejo Antigo & Modão",
    "Reggaeton, Cachengue & Latino",
    "Samba & Pagode",
    "Trap & Rap Nacional",
    "Rock & Pop Nostalgia",
    "Outros"
]

def resolve_official_category(title: str, artist: str = "", default_cat: str = "Outros") -> str:
    text = (str(title) + " " + str(artist)).lower()
    if re.search(r'cumbia|villera|santafesina|charanga|chicha|cuarteto|reggaeton|latino|dembow|perreo|bachata|sonido profesional|fiestero|cachengue|el reja', text):
        return "Reggaeton, Cachengue & Latino"
    if re.search(r'megafunk|mega funk|ritmada|eletrofunk|eletro funk', text):
        return "Mega Funk & Ritmadas"
    if re.search(r'funk|mandel|bh|fluxo|favela|kondzilla|gr6|mc |montagem', text):
        return "Funk Paulista, BH & Mandelão"
    if re.search(r'eletr|house|desande|edm|techno|trance|psy|rave|alok|vintage', text):
        return "Eletrônica, House & Desande"
    if re.search(r'sertanejo|universit|agronejo|modao|modão|gusttavo|jorge|marilia|zeneto', text):
        return "Sertanejo Universitário & Atual"
    if re.search(r'samba|pagode|ferrugem|dilsinho|sorriso maroto|turma do pagode', text):
        return "Samba & Pagode"
    if re.search(r'trap|rap|drill|hip hop|hip-hop|matue|kayblack|veigh|filipe ret', text):
        return "Trap & Rap Nacional"
    if re.search(r'rock|pop|nostalgia|anos 80|anos 90|anos 2000', text):
        return "Rock & Pop Nostalgia"
    return default_cat if default_cat in OFFICIAL_CATEGORIES else "Outros"

def search_tracks(query: str, category: str = "", limit: int = 15) -> dict:
    """Pesquisa livre: busca tanto na biblioteca local (725+ músicas) quanto no YouTube com IA."""
    query = (query or "").strip()
    lib_matches = []
    library_tracks = []
    if LIBRARY_FILE.exists():
        try:
            with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                library_tracks = json.load(f)
        except Exception:
            library_tracks = []

    lib_vids = {t.get("video_id") for t in library_tracks if t.get("video_id")}

    if query:
        import unicodedata
        def strip_acc(s):
            return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn").lower()
        q_words = strip_acc(query).split()
        for t in library_tracks:
            t_str = strip_acc(f"{t.get('title', '')} {t.get('artist', '')} {t.get('category', '')} {t.get('bpm', '')}")
            if all(w in t_str for w in q_words):
                item = dict(t)
                item["in_library"] = True
                lib_matches.append(item)
                if len(lib_matches) >= 50:
                    break

    yt_tracks = []
    if query:
        try:
            yt_tracks = discover_tracks(category or "Personalizada", custom_query=query, limit=limit)
            for t in yt_tracks:
                t["in_library"] = (t.get("video_id") in lib_vids)
                cat = t.get("category")
                if not cat or cat == "Personalizada" or cat not in OFFICIAL_CATEGORIES:
                    t["category"] = resolve_official_category(t.get("title", ""), t.get("artist", ""))
        except Exception as err:
            print("Erro ao buscar novidades no YouTube:", err)
            yt_tracks = []

    combined = list(lib_matches)
    for yt in yt_tracks:
        if not any(c.get("video_id") == yt.get("video_id") for c in combined):
            combined.append(yt)

    return {
        "tracks": combined,
        "library_tracks": lib_matches,
        "youtube_tracks": [t for t in yt_tracks if not t.get("in_library")],
        "count": len(combined)
    }


class MusicServerHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "application/javascript",
        ".mjs": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
        ".ico": "image/x-icon",
        ".html": "text/html",
    }

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_json(self, data, status=200):
        try:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError, OSError):
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path == "/api/history":
                history = []
                history_file = HISTORY_FILE
                if history_file.exists():
                    try:
                        with open(history_file, "r", encoding="utf-8") as f:
                            history = json.load(f)
                    except Exception:
                        history = []
                self.send_json({"history": history})
                return

            if path == "/api/queue":
                self.send_json(load_queue())
                return

            if path == "/api/suggestions":
                suggestions = []
                if SUGGESTIONS_FILE.exists():
                    try:
                        with open(SUGGESTIONS_FILE, "r", encoding="utf-8") as f:
                            suggestions = json.load(f)
                    except Exception:
                        pass
                self.send_json(suggestions)
                return

            if path == "/api/search":
                params = urllib.parse.parse_qs(parsed.query)
                q = params.get("q", [""])[0] or params.get("query", [""])[0]
                cat = params.get("category", [""])[0]
                res = search_tracks(q, cat)
                self.send_json(res)
                return

            if path == "/api/spotify/playlists":
                catalog = {}
                sp_file = Path("spotify_playlists_catalog.json")
                if sp_file.exists():
                    try:
                        with open(sp_file, "r", encoding="utf-8") as f:
                            catalog = json.load(f)
                    except Exception:
                        catalog = {}
                self.send_json(catalog)
                return

            if path == "/api/suggestions/discover":
                params = urllib.parse.parse_qs(parsed.query)
                cat = params.get("category", ["Mega Funk & Ritmadas"])[0]
                tracks = discover_tracks(cat)
                self.send_json({"category": cat, "tracks": tracks, "count": len(tracks)})
                return

            if path == "/api/suggestions/related":
                params = urllib.parse.parse_qs(parsed.query)
                title = params.get("title", [""])[0]
                artist = params.get("artist", [""])[0]
                category = params.get("category", ["Outros"])[0]
                vid = params.get("video_id", [None])[0]
                bpm_val = params.get("bpm", [None])[0]
                target_bpm = int(bpm_val) if bpm_val and bpm_val.isdigit() else None
                tracks = discover_related_tracks(title, artist, category, vid, target_bpm=target_bpm)
                self.send_json({
                    "success": True,
                    "title": title,
                    "artist": artist,
                    "category": category,
                    "target_bpm": target_bpm,
                    "tracks": tracks,
                    "count": len(tracks)
                })
                return

            if path == "/api/audio/stream":
                params = urllib.parse.parse_qs(parsed.query)
                vid = params.get("id", [None])[0]
                if not vid:
                    self.send_error(400, "Missing video id")
                    return
                self.handle_audio_stream(vid)
                return

            if path == "/api/audio/url" or path == "/api/audio/info":
                params = urllib.parse.parse_qs(parsed.query)
                vid = params.get("id", [None])[0]
                if not vid:
                    self.send_json({"error": "Missing video id"}, status=400)
                    return
                info = get_audio_info(vid)
                if info:
                    self.send_json({
                        "video_id": vid,
                        "url": info.get("url"),
                        "duration": info.get("duration", 0),
                        "ext": info.get("ext", "m4a")
                    })
                else:
                    self.send_json({"video_id": vid, "url": None, "duration": 0}, status=404)
                return

            if path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return

            if path == "/" or path == "":
                self.path = "/player.html"

            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError, OSError) as e:
            if isinstance(e, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError)) or getattr(e, "winerror", None) in (10053, 10054):
                return
            import traceback
            traceback.print_exc()
            try:
                self.send_json({"error": str(e)}, status=500)
            except Exception:
                pass
        except Exception as err:
            import traceback
            traceback.print_exc()
            try:
                self.send_json({"error": str(err)}, status=500)
            except Exception:
                pass

    def handle_audio_stream(self, video_id):
        range_hdr = self.headers.get("Range")
        
        for attempt in range(2):
            force_refresh = (attempt > 0)
            info = get_audio_info(video_id, force_refresh=force_refresh)
            if not info or not info.get("url"):
                if attempt == 0:
                    continue
                self.send_error(404, "Audio not found or unavailable")
                return
            
            url = info["url"]
            duration = info.get("duration", 0)
            ext = info.get("ext", "m4a")
            ct_fallback = "audio/mp4" if ext == "m4a" else "audio/webm"
            
            req_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Encoding": "identity",
            }
            if info.get("http_headers"):
                req_headers.update(info["http_headers"])
            if range_hdr:
                req_headers["Range"] = range_hdr
            
            try:
                req = urllib.request.Request(url, headers=req_headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    self.send_response(resp.status)
                    ct = resp.headers.get("Content-Type", ct_fallback)
                    self.send_header("Content-Type", ct)
                    self.send_header("Accept-Ranges", "bytes")
                    if resp.headers.get("Content-Range"):
                        self.send_header("Content-Range", resp.headers.get("Content-Range"))
                    if resp.headers.get("Content-Length"):
                        self.send_header("Content-Length", resp.headers.get("Content-Length"))
                    if duration:
                        self.send_header("X-Audio-Duration", str(duration))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Access-Control-Allow-Methods", "GET, HEAD, OPTIONS")
                    self.send_header("Access-Control-Allow-Headers", "Range, Content-Type")
                    self.send_header("Access-Control-Expose-Headers", "Content-Range, Content-Length, Accept-Ranges, X-Audio-Duration")
                    self.end_headers()

                    while True:
                        chunk = resp.read(131072)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                    return
            except urllib.error.HTTPError as he:
                if he.code in (403, 410) and attempt == 0:
                    print(f"[Stream] HTTP {he.code} (link expirado) para {video_id}. Renovando URL direta do YouTube...")
                    AUDIO_CACHE.pop(video_id, None)
                    continue
                else:
                    print(f"[Stream] HTTPError {he.code} ao reproduzir {video_id}: {he}")
                    try:
                        self.send_error(he.code, f"YouTube CDN Error: {he.code}")
                    except Exception:
                        pass
                    return
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError, OSError) as e:
                if isinstance(e, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError)) or getattr(e, "winerror", None) in (10053, 10054):
                    return
                return
            except Exception as e:
                print(f"[Stream] Erro no stream de {video_id}: {e}")
                try:
                    self.send_error(500, str(e))
                except Exception:
                    pass
                return

    def do_POST(self):
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

            try:
                data = json.loads(post_body.decode("utf-8"))
            except Exception:
                data = {}

            if self.path == "/api/audio/prewarm":
                video_ids = data.get("video_ids", [])
                if isinstance(video_ids, list):
                    prewarm_audio_cache(video_ids[:10])
                self.send_json({"success": True, "count": len(video_ids)})
                return

            if self.path == "/api/queue/add":
                video_id = data.get("video_id")
                title = data.get("title")
                artist = data.get("artist", "")
                category = data.get("category", "Outros")

                if not video_id or not title:
                    self.send_json({"error": "video_id and title required"}, status=400)
                    return

                queue = load_queue()
                if not any(item.get("video_id") == video_id for item in queue):
                    queue.append({
                        "video_id": video_id,
                        "title": title,
                        "artist": artist,
                        "category": category
                    })
                    save_queue(queue)

                self.send_json({"success": True, "count": len(queue), "queue": queue})
                return

            if self.path == "/api/queue/remove":
                video_id = data.get("video_id")
                queue = load_queue()
                queue = [item for item in queue if item.get("video_id") != video_id]
                save_queue(queue)
                self.send_json({"success": True, "count": len(queue), "queue": queue})
                return

            if self.path == "/api/queue/clear":
                save_queue([])
                self.send_json({"success": True, "count": 0, "queue": []})
                return

            if self.path == "/api/suggestions/discover":
                category = data.get("category", "Mega Funk & Ritmadas")
                title = data.get("title", "")
                bpm = data.get("bpm") or detect_or_estimate_bpm(title, category)
                custom_q = data.get("query")
                tracks = discover_tracks(category, custom_query=custom_q, seed_bpm=bpm)
                self.send_json({
                    "success": True,
                    "category": category,
                    "tracks": tracks,
                    "count": len(tracks)
                })
                return

            if self.path == "/api/suggestions/related":
                title = data.get("title", "")
                artist = data.get("artist", "")
                category = data.get("category", "Outros")
                vid = data.get("video_id")
                target_bpm = data.get("bpm")
                if target_bpm and not isinstance(target_bpm, int):
                    try:
                        target_bpm = int(target_bpm)
                    except Exception:
                        target_bpm = None
                tracks = discover_related_tracks(title, artist, category, vid, target_bpm=target_bpm)
                self.send_json({
                    "success": True,
                    "title": title,
                    "artist": artist,
                    "category": category,
                    "target_bpm": target_bpm,
                    "tracks": tracks,
                    "count": len(tracks)
                })
                return

            if self.path == "/api/suggestions/reset-seen":
                if SEEN_FILE.exists():
                    SEEN_FILE.unlink(missing_ok=True)
                self.send_json({"success": True, "message": "Histórico de sugestões resetado com sucesso."})
                return

            if self.path == "/api/search":
                query = data.get("query", "").strip()
                category = data.get("category", "")
                res = search_tracks(query, category)
                self.send_json(res)
                return

            if self.path == "/api/history/add":
                track = data.get("track")
                if not track or not track.get("video_id"):
                    self.send_json({"error": "track required"}, status=400)
                    return
                history_file = HISTORY_FILE
                history = []
                if history_file.exists():
                    try:
                        with open(history_file, "r", encoding="utf-8") as f:
                            history = json.load(f)
                    except Exception:
                        history = []
                if not history or history[0].get("video_id") != track.get("video_id"):
                    cat = track.get("category")
                    if not cat or cat == "Personalizada" or cat not in OFFICIAL_CATEGORIES:
                        track["category"] = resolve_official_category(track.get("title", ""), track.get("artist", ""))
                    history.insert(0, track)
                    history = history[:200]
                    try:
                        with open(history_file, "w", encoding="utf-8") as f:
                            json.dump(history, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print("Erro ao salvar playback_history.json:", e)
                self.send_json({"status": "ok", "count": len(history)})
                return

            if self.path == "/api/history/clear":
                history_file = HISTORY_FILE
                try:
                    with open(history_file, "w", encoding="utf-8") as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print("Erro ao limpar playback_history.json:", e)
                self.send_json({"status": "cleared", "count": 0})
                return

            if self.path == "/api/library/add":
                video_id = data.get("video_id")
                title = data.get("title")
                artist = data.get("artist", "")
                category = data.get("category", "")
                if not category or category == "Personalizada" or category not in OFFICIAL_CATEGORIES:
                    category = resolve_official_category(title, artist)
                source = data.get("source", "Sugestões (Favoritada)")
                bpm = data.get("bpm") or detect_or_estimate_bpm(title, category)

                if not video_id or not title:
                    self.send_json({"error": "video_id and title required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                if not any(t.get("video_id") == video_id for t in lib):
                    new_item = {
                        "title": title,
                        "artist": artist,
                        "category": category,
                        "video_id": video_id,
                        "source": source,
                        "bpm": bpm
                    }
                    lib.insert(0, new_item)
                    try:
                        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                            json.dump(lib, f, ensure_ascii=False, indent=2)
                        import build_full_player
                        build_full_player.rebuild_player_html()
                    except Exception as err:
                        print("Erro ao salvar complete_library.json:", err)

                seen = load_seen_ids()
                seen.add(video_id)
                save_seen_ids(seen)

                self.send_json({
                    "success": True,
                    "video_id": video_id,
                    "title": title,
                    "category": category,
                    "count": len(lib)
                })
                return

            if self.path == "/api/library/remove":
                video_id = data.get("video_id")
                category = data.get("category")
                if not video_id:
                    self.send_json({"error": "video_id required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                initial_len = len(lib)
                # Remove incondicionalmente por video_id para garantir que nunca falhe por divergência de categoria
                lib = [t for t in lib if t.get("video_id") != video_id]
                removed_count = initial_len - len(lib)

                try:
                    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                        json.dump(lib, f, ensure_ascii=False, indent=2)
                    import build_full_player
                    build_full_player.rebuild_player_html()
                except Exception as err:
                    print("Erro ao salvar complete_library.json na remoção:", err)

                self.send_json({
                    "success": True,
                    "removed_count": removed_count,
                    "video_id": video_id,
                    "count": len(lib)
                })
                return

            if self.path == "/api/library/move":
                video_id = data.get("video_id")
                new_category = data.get("new_category")
                old_category = data.get("old_category")
                if not video_id or not new_category:
                    self.send_json({"error": "video_id and new_category required"}, status=400)
                    return

                lib = []
                if LIBRARY_FILE.exists():
                    try:
                        with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
                            lib = json.load(f)
                    except Exception:
                        lib = []

                moved = False
                # 1. Tenta correspondência exata ou por old_category
                for t in lib:
                    if t.get("video_id") == video_id:
                        if not old_category or str(t.get("category")).strip() == str(old_category).strip():
                            t["category"] = new_category
                            moved = True
                            break

                # 2. Fallback: encontra qualquer entrada com video_id e atualiza a categoria
                if not moved:
                    for t in lib:
                        if t.get("video_id") == video_id:
                            t["category"] = new_category
                            moved = True
                            break

                if moved:
                    try:
                        with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
                            json.dump(lib, f, ensure_ascii=False, indent=2)
                        import build_full_player
                        build_full_player.rebuild_player_html()
                    except Exception as err:
                        print("Erro ao salvar complete_library.json na mudança de categoria:", err)

                self.send_json({
                    "success": moved,
                    "video_id": video_id,
                    "new_category": new_category,
                    "count": len(lib)
                })
                return

            if self.path == "/api/sync-youtube":
                def run_sync_bg():
                    try:
                        import subprocess
                        subprocess.run(["python", "sync_pending_queue.py"], capture_output=True, text=True)
                    except Exception as e:
                        print("Erro no background sync:", e)

                threading.Thread(target=run_sync_bg, daemon=True).start()
                queue = load_queue()
                ids = [t.get("video_id") for t in queue if t.get("video_id")][:50]
                playlist_url = f"https://www.youtube.com/watch_videos?video_ids={','.join(ids)}" if ids else "https://www.youtube.com"

                self.send_json({
                    "success": True,
                    "message": "Sincronização iniciada com sua playlist no YouTube!",
                    "queue_count": len(queue),
                    "playlist_url": playlist_url
                })
                return

            self.send_json({"error": "Not found"}, status=404)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError, OSError) as e:
            if isinstance(e, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError)) or getattr(e, "winerror", None) in (10053, 10054):
                return
            import traceback
            traceback.print_exc()
            try:
                self.send_json({"error": str(e)}, status=500)
            except Exception:
                pass
        except Exception as err:
            import traceback
            traceback.print_exc()
            try:
                self.send_json({"error": str(err)}, status=500)
            except Exception:
                pass


class ThreadingMusicServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address):
        exc_type, exc_val, exc_tb = sys.exc_info()
        if exc_type and (
            issubclass(exc_type, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError, ConnectionError))
            or (issubclass(exc_type, OSError) and getattr(exc_val, "winerror", None) in (10053, 10054))
        ):
            # Client closed socket connection prematurely (expected on audio skip/crossfade)
            return
        super().handle_error(request, client_address)


def run_server():
    with ThreadingMusicServer(("", PORT), MusicServerHandler) as httpd:
        print(f"Servidor rodando em http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
