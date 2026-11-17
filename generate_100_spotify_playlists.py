import json
import random
from pathlib import Path

LIBRARY_FILE = Path("complete_library.json")
SPOTIFY_FILE = Path("spotify_playlists_catalog.json")

with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
    library = json.load(f)

# Carrega playlists existentes para preservar as faixas já resolvidas
existing_catalog = {}
if SPOTIFY_FILE.exists():
    try:
        with open(SPOTIFY_FILE, "r", encoding="utf-8") as f:
            existing_catalog = json.load(f)
    except Exception as e:
        print(f"Aviso ao ler {SPOTIFY_FILE}: {e}")

# Indexação das músicas da biblioteca por categorias e palavras-chave
by_cat = {}
for t in library:
    cat = t.get("category", "Outros")
    by_cat.setdefault(cat, []).append(t)

# Definições das 110 playlists editoriais oficiais do Spotify
PLAYLIST_DEFINITIONS = [
    # --- RANKINGS & HITS NACIONAIS / GLOBAIS ---
    {"id": "top_brasil", "name": "Top Brasil", "badge": "🇧🇷 Top Brasil", "icon": "🇧🇷", "genre": "Hits do Brasil", "desc": "A principal playlist com os maiores hits do país: Sertanejo, Funk e Pop.", "bpm": 132, "cats": ["Sertanejo Universitário & Atual", "Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas"]},
    {"id": "top_50_brasil", "name": "Top 50 – Brasil", "badge": "📈 Top 50 Brasil", "icon": "📈", "genre": "Ranking Diário BR", "desc": "O ranking oficial com as músicas mais tocadas no território brasileiro hoje.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual", "Mega Funk & Ritmadas", "Funk Paulista, BH & Mandelão"]},
    {"id": "top_50_mundo", "name": "Top 50 – Mundo", "badge": "🌍 Top 50 Mundo", "icon": "🌍", "genre": "Hits Globais", "desc": "As faixas latinas e internacionais que dominam as paradas globais no momento.", "bpm": 124, "cats": ["Reggaeton, Cachengue & Latino", "Eletrônica, House & Desande"]},
    {"id": "viral_50_brasil", "name": "Viral 50 Brasil", "badge": "🚀 Viral Brasil", "icon": "🚀", "genre": "Virais e Tendências", "desc": "As faixas que mais crescem e viralizam nas redes sociais brasileiras.", "bpm": 134, "cats": ["Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas", "Trap & Rap Nacional"]},
    {"id": "tiktok_hits_brasil", "name": "TikTok Hits Brasil", "badge": "🎵 TikTok Hits", "icon": "📱", "genre": "Dancinhas & Trends", "desc": "As músicas que são trilha sonora de milhões de vídeos e danças no TikTok.", "bpm": 138, "cats": ["Mega Funk & Ritmadas", "Funk Paulista, BH & Mandelão"]},
    {"id": "radar_spotify_brasil", "name": "Radar Spotify Brasil", "badge": "📡 Radar Brasil", "icon": "📡", "genre": "Novas Revelações", "desc": "Artistas emergentes e futuros gigantes da música brasileira.", "bpm": 128, "cats": ["Trap & Rap Nacional", "Sertanejo Universitário & Atual", "Samba & Pagode"]},
    {"id": "hits_da_semana", "name": "Hits da Semana", "badge": "⭐ Hits da Semana", "icon": "⭐", "genre": "Lançamentos Quentes", "desc": "Tudo o que saiu de mais relevante e bombado nos últimos dias.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual", "Eletrônica, House & Desande", "Funk Paulista, BH & Mandelão"]},
    {"id": "brasil_360", "name": "Brasil 360", "badge": "🇧🇷 Brasil 360", "icon": "🎶", "genre": "Todos os Ritmos BR", "desc": "Uma viagem por todos os cantos e sons do Brasil: Sertanejo, Funk, Pagode e Forró.", "bpm": 126, "cats": ["Samba & Pagode", "Sertanejo Universitário & Atual", "Mega Funk & Ritmadas"]},
    {"id": "sucessos_globais", "name": "Sucessos Globais", "badge": "🌐 Sucessos Globais", "icon": "🌐", "genre": "Pop & Latino Internacional", "desc": "Os maiores sucessos que tocam em rádios e baladas pelo mundo todo.", "bpm": 122, "cats": ["Reggaeton, Cachengue & Latino", "Eletrônica, House & Desande"]},
    {"id": "spotify_top_100", "name": "Spotify Top 100 All-Stars", "badge": "👑 Top 100 All-Stars", "icon": "👑", "genre": "Superestrelas", "desc": "Coleção definitiva com os maiores nomes e produções da atualidade.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual", "Funk Paulista, BH & Mandelão", "Eletrônica, House & Desande"]},

    # --- SERTANEJO (UNIVERSITÁRIO, MODÃO, SOFRÊNCIA, CHURRASCO) ---
    {"id": "esquenta_sertanejo", "name": "Esquenta Sertanejo", "badge": "🤠 Esquenta Sertanejo", "icon": "🤠", "genre": "Sertanejo Universitário", "desc": "Seleção forte para churrasco, festa e boteco com grandes sucessos sertanejos.", "bpm": 128, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "modao_raiz", "name": "Modão Raiz Sertanejo", "badge": "🏆 Modão Raiz", "icon": "🏆", "genre": "Modão Clássico", "desc": "Os clássicos brutos de viola e modões que marcaram época nas comitivas.", "bpm": 115, "cats": ["Sertanejo Antigo & Modão"]},
    {"id": "sertanejo_universitario_2026", "name": "Sertanejo Universitário 2026", "badge": "🎓 Universitário 2026", "icon": "🎓", "genre": "Sertanejo Atual", "desc": "O som jovem das arenas, repúblicas e festivais sertanejos do país.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "sofrencia_sertaneja", "name": "Sofrência Sertaneja", "badge": "💔 Sofrência Bruta", "icon": "💔", "genre": "Sofrência & Dor de Cotovelo", "desc": "Letras que tocam o coração com cerveja gelada na mesa do bar.", "bpm": 118, "cats": ["Sertanejo Universitário & Atual", "Sertanejo Antigo & Modão"]},
    {"id": "churrasco_sertanejo", "name": "Churrasco Sertanejo", "badge": "🥩 Churrasco Sertanejo", "icon": "🥩", "genre": "Festa & Churrasco", "desc": "A trilha sonora perfeita para animar a brasa, os amigos e a família.", "bpm": 126, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "potencia_sertaneja", "name": "Potência Sertaneja", "badge": "⚡ Potência Sertaneja", "icon": "⚡", "genre": "Sertanejo de Festival", "desc": "As faixas mais pesadas e potentes tocadas nos maiores palcos do Brasil.", "bpm": 132, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "sertanejo_no_ponto", "name": "Sertanejo no Ponto", "badge": "🎯 No Ponto", "icon": "🎯", "genre": "Seleção Fina Sertaneja", "desc": "No ritmo certo para ouvir no carro, no trabalho ou relaxando no fim de semana.", "bpm": 124, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "sertanejo_bruto", "name": "Sertanejo Bruto", "badge": "🚜 Sertanejo Bruto", "icon": "🚜", "genre": "Agro & Viola", "desc": "Músicas para o homem do campo, cavalgadas e apaixonados pelo estilo bruto.", "bpm": 120, "cats": ["Sertanejo Antigo & Modão"]},
    {"id": "balada_sertaneja", "name": "Balada Sertaneja", "badge": "🎉 Balada Sertaneja", "icon": "🎉", "genre": "Noite & Agito", "desc": "Batidas agitadas e remixes sertanejos para ferver na balada.", "bpm": 134, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "sertanejo_na_fazenda", "name": "Sertanejo na Fazenda", "badge": "🌾 Na Fazenda", "icon": "🌾", "genre": "Clima Rural", "desc": "Vibe de fazenda, natureza, churrasco de chão e muita moda boa.", "bpm": 122, "cats": ["Sertanejo Antigo & Modão", "Sertanejo Universitário & Atual"]},
    {"id": "flashback_sertanejo_90s", "name": "Flashback Sertanejo Anos 90", "badge": "📻 Sertanejo 90s", "icon": "📻", "genre": "Nostalgia Sertaneja", "desc": "Zezé, Leandro & Leonardo, Chitãozinho & Xororó e as relíquias dos anos 90.", "bpm": 116, "cats": ["Sertanejo Antigo & Modão"]},
    {"id": "top_10_sertanejo_semanal", "name": "Top 10 Sertanejo Semanal", "badge": "🔟 Top 10 Sertanejo", "icon": "🔟", "genre": "As 10 Mais Tocadas", "desc": "O resumo semanal com as dez canções sertanejas mais executadas.", "bpm": 128, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "piseiro_2026", "name": "Piseiro 2026", "badge": "🎹 Piseiro 2026", "icon": "🎹", "genre": "Piseiro & Pisadinha", "desc": "Os teclados mais rápidos e dançantes do Nordeste dominando todo o Brasil.", "bpm": 140, "cats": ["Sertanejo Universitário & Atual", "Mega Funk & Ritmadas"]},
    {"id": "pisadinha_piseiro_hits", "name": "Pisadinha & Piseiro Hits", "badge": "🔥 Pisadinha Hits", "icon": "🔥", "genre": "Pisadinha", "desc": "O som dos paredões nordestinos que conquistou as rádios nacionais.", "bpm": 142, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "piseiro_das_vaquejadas", "name": "Piseiro das Vaquejadas", "badge": "🐎 Vaquejada & Piseiro", "icon": "🐎", "genre": "Vaquejada", "desc": "Trilha sonora das grandes vaquejadas, comitivas e festas de gado.", "bpm": 138, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "arrocha_sofrencia", "name": "Arrocha & Sofrência", "badge": "💔 Arrocha Apaixonado", "icon": "💔", "genre": "Arrocha", "desc": "Aquele compasso gostoso do arrocha pra dançar agarradinho e curtir a sofrência.", "bpm": 118, "cats": ["Sertanejo Universitário & Atual"]},
    {"id": "noite_fria_sofrencia", "name": "Noite Fria & Sofrência", "badge": "🌧️ Noite & Sofrência", "icon": "🌧️", "genre": "Acústico & Sentimento", "desc": "Para aquelas noites em que a saudade aperta e só a música compreende.", "bpm": 112, "cats": ["Sertanejo Antigo & Modão", "Sertanejo Universitário & Atual"]},

    # --- FUNK, MANDELÃO & MEGA FUNK ---
    {"id": "funk_hits", "name": "Funk Hits", "badge": "🔥 Funk Hits", "icon": "🔥", "genre": "Funk Paulista & Mandelão", "desc": "Hits de funk mais escutados nas ruas e no streaming.", "bpm": 135, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "mandelao_sp", "name": "Mandelão SP", "badge": "🔊 Mandelão SP", "icon": "🔊", "genre": "Mandelão Pesado", "desc": "Grave no talo, caixas vibrando e a batida característica das ruas de São Paulo.", "bpm": 140, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "mandelao_bh", "name": "Mandelão BH 2026", "badge": "🎛️ BH Mandelão", "icon": "🎛️", "genre": "Funk de Belo Horizonte", "desc": "O funk ritmado e contagiante de Belo Horizonte com batidas inconfundíveis.", "bpm": 138, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "mega_funk_brasil", "name": "Mega Funk Brasil", "badge": "🏎️ Mega Funk BR", "icon": "🏎️", "genre": "Mega Funk & Ritmadas", "desc": "A fusão perfeita do funk com batidas eletrônicas eletrizantes.", "bpm": 145, "cats": ["Mega Funk & Ritmadas"]},
    {"id": "mega_funk_sc", "name": "Mega Funk Santa Catarina", "badge": "🌊 Mega Funk SC", "icon": "🌊", "genre": "Mega Funk Litoral", "desc": "O som que domina o litoral catarinense de Floripa a Balneário Camboriú.", "bpm": 146, "cats": ["Mega Funk & Ritmadas"]},
    {"id": "mega_funk_pr", "name": "Mega Funk Paraná", "badge": "🌲 Mega Funk PR", "icon": "🌲", "genre": "Mega Funk Sul", "desc": "DJs e produtores paranaenses que revolucionaram o ritmo acelerado.", "bpm": 144, "cats": ["Mega Funk & Ritmadas"]},
    {"id": "mega_funk_revoada", "name": "Mega Funk Revoada", "badge": "🍾 Revoada Funk", "icon": "🍾", "genre": "Revoada & Festa", "desc": "Energia máxima para esquentar a noite antes de sair pra pista.", "bpm": 145, "cats": ["Mega Funk & Ritmadas"]},
    {"id": "baile_de_favela", "name": "Baile de Favela", "badge": "🏰 Baile de Favela", "icon": "🏰", "genre": "Funk das Comunidades", "desc": "Os paredões do fluxo tocando as batidas mais autênticas da quebrada.", "bpm": 136, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "ritmada_dos_fluxos", "name": "Ritmada dos Fluxos", "badge": "💥 Fluxo Ritmada", "icon": "💥", "genre": "Ritmada", "desc": "Batida sincopada e envolvente que dita o ritmo nos maiores fluxos.", "bpm": 142, "cats": ["Mega Funk & Ritmadas", "Funk Paulista, BH & Mandelão"]},
    {"id": "ritmadas_de_cria", "name": "Ritmadas de Cria", "badge": "🕶️ De Cria", "icon": "🕶️", "genre": "Funk de Cria", "desc": "Estilo refinado, rimas marcantes e graves que descem redondo.", "bpm": 140, "cats": ["Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas"]},
    {"id": "funk_consciente_reliquias", "name": "Funk Consciente & Relíquias", "badge": "📖 Funk Consciente", "icon": "📖", "genre": "Mensagem & Letra", "desc": "Letras que contam a realidade, sonhos e superação nas comunidades.", "bpm": 130, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "funk_150_bpm_proibidao", "name": "Funk 150 BPM Proibidão", "badge": "⚡ 150 BPM", "icon": "⚡", "genre": "Acelerado 150 BPM", "desc": "Ritmo frenético no tamborzão pra não deixar ninguém parado.", "bpm": 150, "cats": ["Funk Paulista, BH & Mandelão"]},
    {"id": "paredao_funk", "name": "Paredão do Funk", "badge": "📢 Paredão Funk", "icon": "📢", "genre": "Paredão Automotivo", "desc": "Equalizado no limite para tocar nos maiores paredões automotivos.", "bpm": 144, "cats": ["Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas"]},
    {"id": "top_10_funk_semanal", "name": "Top 10 Funk Semanal", "badge": "🔟 Top 10 Funk", "icon": "🔟", "genre": "Os 10 Maiores Hits", "desc": "As dez faixas de funk mais reproduzidas da semana.", "bpm": 138, "cats": ["Funk Paulista, BH & Mandelão"]},

    # --- RAP & TRAP NACIONAL ---
    {"id": "gigantes_rap", "name": "Gigantes do Rap Nacional", "badge": "🎤 Rap Nacional", "icon": "🎤", "genre": "Rap & Trap Nacional", "desc": "Destaques consagrados e novos monstros do rap e trap no Brasil.", "bpm": 140, "cats": ["Trap & Rap Nacional"]},
    {"id": "trap_brasil", "name": "Trap Brasil", "badge": "💎 Trap Brasil", "icon": "💎", "genre": "Trap Nacional", "desc": "808 distorcido, flow veloz e rimas afiadas da cena trap BR.", "bpm": 142, "cats": ["Trap & Rap Nacional"]},
    {"id": "trapperz_brasil", "name": "Trapperz Brasil", "badge": "🧢 Trapperz", "icon": "🧢", "genre": "Novos Produtores & MCs", "desc": "A nova safra de trappers dominando o streaming com visual e estética.", "bpm": 138, "cats": ["Trap & Rap Nacional"]},
    {"id": "trap_drill_nacional", "name": "Trap & Drill Nacional", "badge": "⚔️ Drill Brasil", "icon": "⚔️", "genre": "Drill & Trap Pesado", "desc": "Sliding 808s, hi-hats sincopados e a agressividade elegante do Drill.", "bpm": 144, "cats": ["Trap & Rap Nacional"]},
    {"id": "trap_melodico_brasil", "name": "Trap Melódico Brasil", "badge": "🌌 Trap Melódico", "icon": "🌌", "genre": "Melodic Trap & Auto-tune", "desc": "Guitarras melancólicas, vocais suaves e melodias envolventes.", "bpm": 130, "cats": ["Trap & Rap Nacional"]},
    {"id": "flow_espacial", "name": "Flow Espacial", "badge": "🛸 Flow Espacial", "icon": "🛸", "genre": "Lofi & Space Trap", "desc": "Produções com sintetizadores etéreos, viagens sonoras e rimas lentas.", "bpm": 125, "cats": ["Trap & Rap Nacional"]},
    {"id": "poesia_acustica_vibes", "name": "Poesia Acústica & Vibes", "badge": "🎸 Poesia Acústica", "icon": "🎸", "genre": "Rap Acústico", "desc": "Violões intimistas e duetos poéticos que conquistaram multidões.", "bpm": 115, "cats": ["Trap & Rap Nacional"]},
    {"id": "rimas_poesia", "name": "Rimas & Poesia", "badge": "✍️ Rimas & Poesia", "icon": "✍️", "genre": "Lyrical Hip Hop", "desc": "Poesia em forma de rap com letras profundas e batidas cadenciadas.", "bpm": 120, "cats": ["Trap & Rap Nacional"]},
    {"id": "hip_hop_brasil_classicos", "name": "Hip Hop Brasil Clássicos", "badge": "👑 Clássicos Hip Hop", "icon": "👑", "genre": "Boom Bap Raiz", "desc": "As origens do hip hop brasileiro: batidas cruas e mensagens imortais.", "bpm": 95, "cats": ["Trap & Rap Nacional"]},
    {"id": "top_10_rap_trap_semanal", "name": "Top 10 Rap & Trap Semanal", "badge": "🔟 Top 10 Rap", "icon": "🔟", "genre": "Destaques da Semana", "desc": "As dez músicas de rap e trap que mais subiram no ranking.", "bpm": 138, "cats": ["Trap & Rap Nacional"]},

    # --- PAGODE & SAMBA ---
    {"id": "pagodeira_hits", "name": "Pagodeira Hits", "badge": "🥁 Pagodeira Hits", "icon": "🥁", "genre": "Pagode Moderno", "desc": "Os maiores sucessos do pagode atual que agitam qualquer rodada.", "bpm": 118, "cats": ["Samba & Pagode"]},
    {"id": "churrasquinho_dos_crias", "name": "Churrasquinho dos Crias", "badge": "🍢 Churrasquinho Pagode", "icon": "🍢", "genre": "Pagode & Resenha", "desc": "Cavaquinho estalando, pandeiro no ritmo e aquela carne no ponto.", "bpm": 116, "cats": ["Samba & Pagode"]},
    {"id": "resenha_de_pagode", "name": "Resenha de Pagode", "badge": "🍻 Resenha Pagode", "icon": "🍻", "genre": "Roda de Amigos", "desc": "A resenha perfeita com amigos cantando junto todos os refrões.", "bpm": 115, "cats": ["Samba & Pagode"]},
    {"id": "samba_de_raiz", "name": "Samba de Raiz", "badge": "🌺 Samba Raiz", "icon": "🌺", "genre": "Samba Tradicional", "desc": "O verdadeiro samba carioca e paulista com respeito às velhas guardas.", "bpm": 110, "cats": ["Samba & Pagode"]},
    {"id": "tardezinha_pagode", "name": "Tardezinha Pagode", "badge": "🌅 Tardezinha", "icon": "🌅", "genre": "Pagode Sunset", "desc": "Clima de final de tarde ao som dos grupos mais amados do país.", "bpm": 120, "cats": ["Samba & Pagode"]},
    {"id": "pagode_romantico_90s", "name": "Pagode Romântico 90s & 2000s", "badge": "💖 Pagode 90s & 2000s", "icon": "💖", "genre": "Romântico Nostalgia", "desc": "As canções de amor inesquecíveis que todo mundo sabe a letra de cor.", "bpm": 112, "cats": ["Samba & Pagode"]},
    {"id": "sambinha_cerveja_gelada", "name": "Sambinha & Cerveja Gelada", "badge": "🍺 Sambinha & Breja", "icon": "🍺", "genre": "Descontração", "desc": "Clima leve de boteco com samba de primeira e um copo bem gelado.", "bpm": 114, "cats": ["Samba & Pagode"]},
    {"id": "domingo_de_pagode", "name": "Domingo de Pagode", "badge": "☀️ Domingo Pagode", "icon": "☀️", "genre": "Fim de Semana", "desc": "Domingo não é domingo sem aquele pagodinho gostoso pra relaxar.", "bpm": 116, "cats": ["Samba & Pagode"]},
    {"id": "pagode_churrasco_parcas", "name": "Pagode e Churrasco dos Parças", "badge": "🤝 Dos Parças", "icon": "🤝", "genre": "Confraternização", "desc": "Reunir a galera, colocar o pagode pra rolar e esquecer dos boletos.", "bpm": 118, "cats": ["Samba & Pagode"]},
    {"id": "top_10_pagode_semanal", "name": "Top 10 Pagode Semanal", "badge": "🔟 Top 10 Pagode", "icon": "🔟", "genre": "Os 10 Mais Pedidos", "desc": "Os dez maiores destaques de pagode da semana.", "bpm": 116, "cats": ["Samba & Pagode"]},

    # --- ELETRÔNICA, HOUSE & DESANDE ---
    {"id": "eletronica_brasil", "name": "Eletrônica Brasil", "badge": "⚡ Eletrônica BR", "icon": "⚡", "genre": "Dance & Club BR", "desc": "Os principais produtores nacionais que colocam multidões para dançar.", "bpm": 126, "cats": ["Eletrônica, House & Desande"]},
    {"id": "brazilian_bass_club", "name": "Brazilian Bass Club", "badge": "🎛️ Brazilian Bass", "icon": "🎛️", "genre": "Bassline Pesado", "desc": "Graves profundos e linhas de baixo marcantes que definiram o som BR.", "bpm": 125, "cats": ["Eletrônica, House & Desande"]},
    {"id": "desande_low_bass", "name": "Desande & Low Bass", "badge": "🕶️ O Famoso Desande", "icon": "🕶️", "genre": "Desande", "desc": "Goiânia exportando o som do desande com drop seco e batida contagiante.", "bpm": 128, "cats": ["Eletrônica, House & Desande"]},
    {"id": "tech_house_brasil", "name": "Tech House Brasil", "badge": "🎚️ Tech House BR", "icon": "🎚️", "genre": "Clubbing & Underground", "desc": "Grooves sofisticados para pistas fechadas e after-hours.", "bpm": 127, "cats": ["Eletrônica, House & Desande"]},
    {"id": "deep_house_sunset", "name": "Deep House Sunset", "badge": "🌇 Deep Sunset", "icon": "🌇", "genre": "Deep House Melódico", "desc": "Melodias suaves e batidas envolventes para apreciar o pôr do sol.", "bpm": 122, "cats": ["Eletrônica, House & Desande"]},
    {"id": "vintage_culture_friends", "name": "Vintage Culture & Friends", "badge": "🎩 Vintage Vibes", "icon": "🎩", "genre": "Vibe de Festival", "desc": "Sets enérgicos e produções consagradas nos maiores festivais do planeta.", "bpm": 126, "cats": ["Eletrônica, House & Desande"]},
    {"id": "alok_anthems", "name": "Alok Anthems", "badge": "🎧 Alok & Parcerias", "icon": "🎧", "genre": "Mainstage EDM", "desc": "As produções e colaborações globais do DJ número um do Brasil.", "bpm": 125, "cats": ["Eletrônica, House & Desande"]},
    {"id": "edm_festival_brasil", "name": "EDM Festival Brasil", "badge": "🎪 EDM Festival", "icon": "🎪", "genre": "Mainstage & Drops", "desc": "Toda a energia dos palcos principais com drops eletrizantes.", "bpm": 128, "cats": ["Eletrônica, House & Desande"]},
    {"id": "balada_eletronica", "name": "Balada Eletrônica", "badge": "✨ Balada Eletrônica", "icon": "✨", "genre": "Noite Toda", "desc": "Faixas contínuas que mantêm o público na pista até o amanhecer.", "bpm": 126, "cats": ["Eletrônica, House & Desande"]},
    {"id": "top_10_eletronica_semanal", "name": "Top 10 Eletrônica Semanal", "badge": "🔟 Top 10 Dance", "icon": "🔟", "genre": "Top 10 Eletrônica", "desc": "As dez faixas eletrônicas mais tocadas nas plataformas.", "bpm": 126, "cats": ["Eletrônica, House & Desande"]},

    # --- REGGAETON, LATINO & CACHENGUE ---
    {"id": "reggaeton_caliente", "name": "Reggaeton Caliente", "badge": "🌴 Reggaeton Caliente", "icon": "🌴", "genre": "Dembow & Perreo", "desc": "O som que não deixa ninguém parado: dembow intenso e puro perreo latino.", "bpm": 96, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "latino_gang", "name": "Latino Gang", "badge": "💎 Latino Gang", "icon": "💎", "genre": "Trap Latino & Pop", "desc": "Bad Bunny, Karol G, Feid, Rauw Alejandro e as estrelas da música latina.", "bpm": 100, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "cachengue_rkt_argentina", "name": "Cachengue & RKT Argentina", "badge": "🇦🇷 Cachengue & RKT", "icon": "🇦🇷", "genre": "RKT Argentino", "desc": "O fenômeno do RKT e cachengue argentino que invadiu as festas de todo o continente.", "bpm": 102, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "bailando_reggaeton", "name": "Bailando Reggaeton", "badge": "💃 Bailando", "icon": "💃", "genre": "Fiesta Latina", "desc": "Clima de festa caribenha, bebidas tropicais e pista cheia de energia.", "bpm": 98, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "fuego_latino", "name": "Fuego Latino", "badge": "🔥 Fuego Latino", "icon": "🔥", "genre": "Hits Latinos Atuais", "desc": "Os lançamentos mais quentes das paradas da América Latina e Espanha.", "bpm": 98, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "urban_latino_hits", "name": "Urban Latino Hits", "badge": "🌆 Urban Latino", "icon": "🌆", "genre": "Música Urbana", "desc": "Batidas urbanas de Porto Rico, Colômbia e México para ouvir no último volume.", "bpm": 102, "cats": ["Reggaeton, Cachengue & Latino"]},
    {"id": "top_10_latino_semanal", "name": "Top 10 Latino Semanal", "badge": "🔟 Top 10 Latino", "icon": "🔟", "genre": "Ranking Latino", "desc": "As dez faixas latinas mais tocadas da semana.", "bpm": 98, "cats": ["Reggaeton, Cachengue & Latino"]},

    # --- ROCK, POP & FLASHBACK ---
    {"id": "rock_brasil_80_90", "name": "Rock Brasil 80 & 90", "badge": "🎸 Rock BR 80/90", "icon": "🎸", "genre": "Rock Nacional", "desc": "Legião Urbana, Titãs, Paralamas, Barão Vermelho e os hinos do rock nacional.", "bpm": 120, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "classicos_rock_nacional", "name": "Clássicos do Rock Nacional", "badge": "⚡ Rock Clássico", "icon": "⚡", "genre": "Guitarras e Refrões", "desc": "Músicas que marcaram gerações e continuam vivas no coração dos fãs.", "bpm": 125, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "pop_brasil_2000", "name": "Pop Brasil 2000", "badge": "📀 Pop Anos 2000", "icon": "📀", "genre": "Pop Anos 2000", "desc": "A era de ouro das boy bands, divas pop e sucessos de rádio dos anos 2000.", "bpm": 118, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "flashback_80s_90s_brasil", "name": "Flashback 80s 90s Brasil", "badge": "📻 Flashback Total", "icon": "📻", "genre": "Flashback Épico", "desc": "Uma máquina do tempo musical com os maiores clássicos dos anos 80 e 90.", "bpm": 120, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "mpb_classicos_novidades", "name": "MPB Clássicos & Novidades", "badge": "🍃 MPB Brasil", "icon": "🍃", "genre": "Música Popular Brasileira", "desc": "A riqueza lírica e harmônica dos grandes compositores brasileiros.", "bpm": 105, "cats": ["Rock & Pop Nostalgia", "Samba & Pagode"]},
    {"id": "acustico_mpb", "name": "Acústico MPB", "badge": "☕ Acústico MPB", "icon": "☕", "genre": "Voz & Violão Suave", "desc": "Arranjos intimistas de voz e violão para acalmar a mente e o coração.", "bpm": 100, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "barzinho_violao", "name": "Barzinho & Violão", "badge": "🍷 Barzinho & Violão", "icon": "🍷", "genre": "Clima de Boteco Acústico", "desc": "Aquela sensação nostálgica de estar no bar preferido ouvindo boa música ao vivo.", "bpm": 108, "cats": ["Rock & Pop Nostalgia", "Sertanejo Antigo & Modão"]},
    {"id": "e_o_tchan_axe_90s", "name": "É O Tchan & Axé 90s", "badge": "🥁 Axé Bahia 90s", "icon": "🥁", "genre": "Axé Music Retrô", "desc": "O suingue contagiante do axé que levantou o Brasil na década de 90.", "bpm": 130, "cats": ["Samba & Pagode", "Mega Funk & Ritmadas"]},
    {"id": "micareta_hits", "name": "Micareta Hits", "badge": "🎉 Micareta Hits", "icon": "🎉", "genre": "Carnaval Fora de Época", "desc": "Puxando trio elétrico, cantando junto e pulando sem parar.", "bpm": 135, "cats": ["Samba & Pagode", "Mega Funk & Ritmadas"]},
    {"id": "pop_hits_brasil", "name": "Pop Hits Brasil", "badge": "🌟 Pop Brasil", "icon": "🌟", "genre": "Pop Moderno BR", "desc": "Os cantores e cantoras pop que dominam as redes e rádios do Brasil.", "bpm": 122, "cats": ["Sertanejo Universitário & Atual", "Reggaeton, Cachengue & Latino"]},

    # --- MOMENTOS, VIBES & ACADEMIA (TREINO, CHILL, ESTRADA) ---
    {"id": "treino_pesado_motivacao", "name": "Treino Pesado (Motivação)", "badge": "🏋️ Treino Pesado", "icon": "🏋️", "genre": "Pump & Foco", "desc": "Músicas de alta energia para superar os próprios limites na musculação.", "bpm": 140, "cats": ["Trap & Rap Nacional", "Eletrônica, House & Desande"]},
    {"id": "treino_funk_150_bpm", "name": "Treino Funk 150 BPM", "badge": "🏃 Cardio 150 BPM", "icon": "🏃", "genre": "Cardio Acelerado", "desc": "Batida acelerada para corrida, esteira e queima máxima de calorias.", "bpm": 150, "cats": ["Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas"]},
    {"id": "treino_trap_rap", "name": "Treino Trap & Rap", "badge": "🥊 Trap Treino", "icon": "🥊", "genre": "Foco & Peso", "desc": "Graves poderosos e rimas inspiradoras para manter o ritmo forte.", "bpm": 142, "cats": ["Trap & Rap Nacional"]},
    {"id": "academia_hardcore", "name": "Academia Hardcore", "badge": "💥 Academia Hardcore", "icon": "💥", "genre": "Treino Extremo", "desc": "Para os dias de treino mais intenso em que você precisa de sangue nos olhos.", "bpm": 145, "cats": ["Mega Funk & Ritmadas", "Eletrônica, House & Desande"]},
    {"id": "treino_eletronica_low_bass", "name": "Treino Eletrônica Low Bass", "badge": "⚡ Bass Treino", "icon": "⚡", "genre": "Bass Motivation", "desc": "Batida constante e pulsante que te carrega de repetição em repetição.", "bpm": 128, "cats": ["Eletrônica, House & Desande"]},
    {"id": "sunset_vibes_brasil", "name": "Sunset Vibes Brasil", "badge": "🌅 Sunset Vibes", "icon": "🌅", "genre": "Fim de Tarde", "desc": "Trilha sonora perfeita para o pôr do sol na praia ou na varanda.", "bpm": 122, "cats": ["Eletrônica, House & Desande", "Samba & Pagode"]},
    {"id": "pool_party_hits", "name": "Pool Party Hits", "badge": "🏊 Pool Party", "icon": "🏊", "genre": "Festa na Piscina", "desc": "Sol, água refrescante, amigos reunidos e música alegre o dia todo.", "bpm": 126, "cats": ["Eletrônica, House & Desande", "Reggaeton, Cachengue & Latino"]},
    {"id": "resenha_com_amigos", "name": "Resenha com os Amigos", "badge": "🍻 Resenha Amigos", "icon": "🍻", "genre": "Bate-Papo & Risadas", "desc": "Para colocar de fundo enquanto rola aquela boa conversa e descontração.", "bpm": 120, "cats": ["Sertanejo Universitário & Atual", "Samba & Pagode"]},
    {"id": "na_estrada_road_trip", "name": "Na Estrada (Road Trip Brasil)", "badge": "🛣️ Na Estrada", "icon": "🛣️", "genre": "Viagem & Carro", "desc": "Janela aberta, vento no rosto e as melhores músicas para acompanhar a viagem.", "bpm": 124, "cats": ["Sertanejo Universitário & Atual", "Rock & Pop Nostalgia"]},
    {"id": "churrasco_no_sitio", "name": "Churrasco no Sítio", "badge": "🏡 No Sítio", "icon": "🏡", "genre": "Festa no Campo", "desc": "Aconchego, ar puro e música que todo mundo canta e aprova.", "bpm": 122, "cats": ["Sertanejo Universitário & Atual", "Sertanejo Antigo & Modão"]},
    {"id": "almoco_de_domingo", "name": "Almoço de Domingo", "badge": "🍝 Almoço Domingo", "icon": "🍝", "genre": "Família & Reunião", "desc": "Trilha sonora gostosa para o almoço em família com harmonia e alegria.", "bpm": 115, "cats": ["Sertanejo Antigo & Modão", "Samba & Pagode"]},
    {"id": "relaxing_acoustic_vibes", "name": "Relaxing Acoustic Vibes", "badge": "🌿 Relax Acústico", "icon": "🌿", "genre": "Relax & Desacelerar", "desc": "Sons suaves para ler um livro, trabalhar com foco ou simplesmente relaxar.", "bpm": 105, "cats": ["Rock & Pop Nostalgia"]},
    {"id": "lofi_beats_brasil", "name": "Lofi Beats Brasil", "badge": "☕ Lofi Brasil", "icon": "☕", "genre": "Estudo & Foco", "desc": "Batidas lo-fi aconchegantes com toques de bossa nova e beats urbanos.", "bpm": 85, "cats": ["Rock & Pop Nostalgia", "Trap & Rap Nacional"]},
    {"id": "chillout_lounge_coffee", "name": "Chillout Lounge & Coffee", "badge": "🥐 Lounge & Café", "icon": "🥐", "genre": "Cafeteria & Ambiente", "desc": "Ambiente elegante e moderno para degustar um café e relaxar a mente.", "bpm": 108, "cats": ["Eletrônica, House & Desande"]},
    {"id": "sextou_brasil", "name": "Sextou Brasil", "badge": "🍻 Sextou!", "icon": "🍻", "genre": "Início do Final de Semana", "desc": "Deu a hora de fechar o expediente e começar a curtir a melhor época da semana.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual", "Funk Paulista, BH & Mandelão"]},
    {"id": "pre_balada_hits", "name": "Pré-Balada Hits", "badge": "💄 Pré-Balada", "icon": "💄", "genre": "Esquenta Antes da Noite", "desc": "Se arrumando com os amigos e aumentando a energia para a balada.", "bpm": 132, "cats": ["Mega Funk & Ritmadas", "Funk Paulista, BH & Mandelão", "Eletrônica, House & Desande"]},
    {"id": "bailao_automotivo", "name": "Bailão Automotivo", "badge": "🔊 Som Automotivo", "icon": "🔊", "genre": "Som Pesado na Mala", "desc": "Mala aberta, cornetas afinadas e grave empurrando o ar.", "bpm": 142, "cats": ["Funk Paulista, BH & Mandelão", "Mega Funk & Ritmadas"]},
    {"id": "carro_de_som_brasil", "name": "Carro de Som Brasil", "badge": "🚗 Carro de Som", "icon": "🚗", "genre": "Graves Extremos", "desc": "Produzido especialmente para quem ama sentir o grave no peito dentro do carro.", "bpm": 144, "cats": ["Mega Funk & Ritmadas", "Funk Paulista, BH & Mandelão"]},
    {"id": "paredao_200_bass", "name": "Paredão 200% Bass", "badge": "🚀 200% Bass Boost", "icon": "🚀", "genre": "Bass Extremo VLC", "desc": "Graves reforçados para testar toda a potência do sistema de áudio HD.", "bpm": 146, "cats": ["Mega Funk & Ritmadas", "Eletrônica, House & Desande"]},
    {"id": "top_brasil_sunset", "name": "Top Brasil Sunset", "badge": "🌇 Brasil Sunset", "icon": "🌇", "genre": "Sucessos ao Pôr do Sol", "desc": "Os maiores sucessos do país em roupagem descontraída para o fim de tarde.", "bpm": 125, "cats": ["Sertanejo Universitário & Atual", "Eletrônica, House & Desande"]},
    {"id": "top_10_mega_funk_semanal", "name": "Top 10 Mega Funk Semanal", "badge": "🔟 Top 10 Mega Funk", "icon": "🔟", "genre": "Os 10 Mais Rápidos", "desc": "As dez faixas de mega funk mais bombadas da semana.", "bpm": 146, "cats": ["Mega Funk & Ritmadas"]},
    {"id": "top_brasil_2026", "name": "Top Brasil 2026", "badge": "🌟 Brasil 2026", "icon": "🌟", "genre": "Lançamentos 2026", "desc": "As canções que definem o ano de 2026 nos fones e caixas do país.", "bpm": 130, "cats": ["Sertanejo Universitário & Atual", "Funk Paulista, BH & Mandelão"]},
    {"id": "trap_funk_brasil", "name": "Trap Funk Brasil", "badge": "🔥 Trap Funk", "icon": "🔥", "genre": "Trap Funk Fusion", "desc": "A fusão perfeita do flow do trap com a pressão dos graves do funk.", "bpm": 138, "cats": ["Trap & Rap Nacional", "Funk Paulista, BH & Mandelão"]}
]

print(f"Total de definições de playlists: {len(PLAYLIST_DEFINITIONS)}")

new_catalog = {}

for pl in PLAYLIST_DEFINITIONS:
    pl_id = pl["id"]
    existing = existing_catalog.get(pl_id)
    
    # Se já existia e tinha faixas com YouTube ID real, reaproveita prioritariamente
    if existing and existing.get("tracks") and len(existing["tracks"]) >= 5:
        # Atualiza metadados com descrição/ícones atualizados
        existing_meta = existing.get("meta", {})
        merged_meta = {
            "id": pl_id,
            "name": pl["name"],
            "badge": pl["badge"],
            "icon": pl["icon"],
            "genre": pl["genre"],
            "desc": pl["desc"],
            "bpm": pl["bpm"]
        }
        # Garante que cada faixa tem categoria e playlist_id corretos
        tracks = []
        for i, t in enumerate(existing["tracks"], 1):
            tracks.append({
                "rank": i,
                "title": t.get("title", ""),
                "artist": t.get("artist", ""),
                "category": pl["name"],
                "playlist_id": pl_id,
                "playlist_badge": pl["badge"],
                "video_id": t.get("video_id", "dQw4w9WgXcQ"),
                "duration": t.get("duration", 180),
                "bpm": t.get("bpm", pl["bpm"]),
                "source": f"Spotify - {pl['name']}"
            })
        new_catalog[pl_id] = {
            "meta": merged_meta,
            "tracks": tracks
        }
        continue

    # Seleciona faixas da biblioteca com base nas categorias mapeadas
    candidate_tracks = []
    for cat in pl["cats"]:
        candidate_tracks.extend(by_cat.get(cat, []))
    
    if not candidate_tracks:
        candidate_tracks = library[:]
    
    # Embaralha de forma pseudo-aleatória determinística pelo nome da playlist
    rng = random.Random(pl_id)
    selected = rng.sample(candidate_tracks, min(len(candidate_tracks), rng.randint(12, 22)))
    
    tracks = []
    for i, t in enumerate(selected, 1):
        tracks.append({
            "rank": i,
            "title": t.get("title", ""),
            "artist": t.get("artist", ""),
            "category": pl["name"],
            "playlist_id": pl_id,
            "playlist_badge": pl["badge"],
            "video_id": t.get("video_id", ""),
            "duration": 180,
            "bpm": t.get("bpm", pl["bpm"]),
            "source": f"Spotify - {pl['name']}"
        })
    
    meta = {
        "id": pl_id,
        "name": pl["name"],
        "badge": pl["badge"],
        "icon": pl["icon"],
        "genre": pl["genre"],
        "desc": pl["desc"],
        "bpm": pl["bpm"]
    }
    
    new_catalog[pl_id] = {
        "meta": meta,
        "tracks": tracks
    }

with open(SPOTIFY_FILE, "w", encoding="utf-8") as f:
    json.dump(new_catalog, f, ensure_ascii=False, indent=2)

print(f"Sucesso! Geradas {len(new_catalog)} playlists oficiais do Spotify em {SPOTIFY_FILE}!")
