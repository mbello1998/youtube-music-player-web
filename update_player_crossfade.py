import json
from pathlib import Path

LIBRARY_FILE = Path("complete_library.json")
SPOTIFY_FILE = Path("spotify_playlists_catalog.json")

if not LIBRARY_FILE.exists():
    raise FileNotFoundError("complete_library.json not found")

with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
    library = json.load(f)

spotify_catalog = {}
if SPOTIFY_FILE.exists():
    try:
        with open(SPOTIFY_FILE, "r", encoding="utf-8") as f:
            spotify_catalog = json.load(f)
    except Exception as e:
        print(f"Aviso ao ler {SPOTIFY_FILE}: {e}")

CATEGORY_ORDER = [
    "Mega Funk & Ritmadas",
    "Funk Paulista, BH & Mandelão",
    "Eletrônica, House & Desande",
    "Sertanejo Universitário & Atual",
    "Sertanejo Antigo & Modão",
    "Reggaeton, Cachengue & Latino",
    "Samba & Pagode",
    "Trap & Rap Nacional",
    "Rock & Pop Nostalgia",
    "Outros",
]

CATEGORY_ICONS = {
    "Mega Funk & Ritmadas": "🔥",
    "Funk Paulista, BH & Mandelão": "🔊",
    "Eletrônica, House & Desande": "⚡",
    "Sertanejo Universitário & Atual": "🤠",
    "Sertanejo Antigo & Modão": "🏆",
    "Reggaeton, Cachengue & Latino": "🌴",
    "Samba & Pagode": "🥁",
    "Trap & Rap Nacional": "🎤",
    "Rock & Pop Nostalgia": "🎸",
    "Outros": "🎧",
}

grouped = {}
for cat in CATEGORY_ORDER:
    grouped[cat] = [t for t in library if t.get("category") == cat and t.get("video_id")]

import re
def resolve_cat(title, artist=""):
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
    return "Outros"

for t in library:
    if t.get("video_id") and t.get("category") not in CATEGORY_ORDER:
        resolved = resolve_cat(t.get("title", ""), t.get("artist", ""))
        t["category"] = resolved
        if resolved in grouped:
            grouped[resolved].append(t)
        else:
            grouped["Outros"].append(t)

with open("player_template.html", "r", encoding="utf-8") as f:
    template = f.read()

html_content = template \
    .replace("__LIBRARY_COUNT__", str(len(library))) \
    .replace("__SPOTIFY_COUNT__", f"{len(spotify_catalog)} Playlists") \
    .replace("__SPOTIFY_COUNT_NUM__", str(len(spotify_catalog))) \
    .replace("__DATA_JSON__", json.dumps(grouped, ensure_ascii=False)) \
    .replace("__ICONS_JSON__", json.dumps(CATEGORY_ICONS, ensure_ascii=False)) \
    .replace("__CATEGORIES_JSON__", json.dumps(CATEGORY_ORDER, ensure_ascii=False)) \
    .replace("__SPOTIFY_PLAYLISTS_JSON__", json.dumps(spotify_catalog, ensure_ascii=False))

with open("player.html", "w", encoding="utf-8") as f:
    f.write(html_content)

with open("generate_perfect_player.py", "w", encoding="utf-8") as f:
    with open(__file__, "r", encoding="utf-8") as src:
        f.write(src.read())

with open("update_player_crossfade.py", "w", encoding="utf-8") as f:
    with open(__file__, "r", encoding="utf-8") as src:
        f.write(src.read())

print(f"Build concluído com sucesso: player.html gerado ({len(html_content)} bytes)!")
