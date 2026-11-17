from igtoyt.categorize import categorize_song


def test_categorize_eletronica():
    assert categorize_song("DANGER DANGER", "Dom Dolla, Solomun, Skepta") == "Eletrônica"
    assert categorize_song("Living on My Own", "illusionize, FEZZO") == "Eletrônica"
    assert categorize_song("Show Me The Way", "Vintage Culture, FM LAETI, Shapeless") == "Eletrônica"


def test_categorize_sertanejo():
    assert categorize_song("Saudade Estranha - Du Nada", "Murilo Huff") == "Sertanejo & Forró"
    assert categorize_song("Esqueci / Amor à Três", "Bruno & Marrone") == "Sertanejo & Forró"
    assert categorize_song("Paredes", "Jorge & Mateus") == "Sertanejo & Forró"
    assert categorize_song("Troca de Tiro", "Grupo Bailaço") == "Sertanejo & Forró"


def test_categorize_funk():
    assert categorize_song("Notificação no Tela", "MC Ryan SP, MC Meno K, DJ Japa NK") == "Funk & Mega Funk"
    assert categorize_song("Mega Funk Good", "TOMAS, Sanchezz DJ") == "Funk & Mega Funk"
    assert categorize_song("Fala na Cara", "Mc Paiva ZS, DJ Ak beats") == "Funk & Mega Funk"


def test_categorize_trap_rap():
    assert categorize_song("Anos Luz", "Matuê") == "Trap & Rap"
    assert categorize_song("tipo, sonho de consumo!", "Kyan, Mu540, Tasha & Tracie") == "Trap & Rap"
    assert categorize_song("SOLTO", "Djonga, Hot, Coyote Beatz") == "Trap & Rap"


def test_categorize_reggaeton_latino():
    assert categorize_song("Hasta el Amanecer", "Nicky Jam") == "Reggaeton & Latino"
    assert categorize_song("Gato de Noche", "Ñengo Flow, Bad Bunny") == "Reggaeton & Latino"


def test_categorize_rock_pop():
    assert categorize_song("How You Remind Me", "Nickelback") == "Rock & Pop"
    assert categorize_song("Faint", "Linkin Park") == "Rock & Pop"


def test_categorize_unknown_fallback():
    assert categorize_song("Música Totalmente Desconhecida", "Artista Desconhecido") == "Outros"
