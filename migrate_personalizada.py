import json
import re

def resolve_category(title: str, artist: str = "") -> str:
    text = (title + " " + artist).lower()
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

with open("complete_library.json", "r", encoding="utf-8") as f:
    lib = json.load(f)

migrated = 0
for t in lib:
    if t.get("category") == "Personalizada" or not t.get("category"):
        new_cat = resolve_category(t.get("title", ""), t.get("artist", ""))
        print(f"Migrando: '{t.get('title')}' -> {new_cat}")
        t["category"] = new_cat
        migrated += 1

with open("complete_library.json", "w", encoding="utf-8") as f:
    json.dump(lib, f, ensure_ascii=False, indent=2)

print(f"\nSucesso: {migrated} faixas migradas para categorias oficiais da biblioteca!")
