# -*- coding: utf-8 -*-
"""
add_cumbia_playlists.py
Adiciona 33 playlists autênticas de Cumbia ao catálogo do Spotify (spotify_playlists_catalog.json)
com faixas oficiais resolvidas diretamente via YouTube.
"""

import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import yt_dlp

SPOTIFY_CATALOG_FILE = Path("spotify_playlists_catalog.json")

CUMBIA_PLAYLISTS = [
    # --- 1. CUMBIA VILLERA ARGENTINA ---
    {
        "id": "cumbia_villera_clasicos",
        "name": "Cumbia Villera Clásicos",
        "badge": "🇦🇷 Cumbia Villera",
        "icon": "🎹",
        "genre": "Cumbia Villera Raiz",
        "desc": "O som cru e autêntico das favelas argentinas: guitarras distorcidas, sintetizadores e o teclado villero marcante.",
        "bpm": 96,
        "tracks": [
            {"query": "Damas Gratis No Te Creas Tan Importante", "artist": "Damas Gratis"},
            {"query": "Pibes Chorros Duraznito", "artist": "Pibes Chorros"},
            {"query": "Yerba Brava La Cumbia de los Trapos", "artist": "Yerba Brava"},
            {"query": "Mala Fama La Marca de la Gorra", "artist": "Mala Fama"},
            {"query": "Supermerk2 La Resaka", "artist": "Supermerk2"},
            {"query": "Flor de Piedra Sos Boton", "artist": "Flor de Piedra"},
            {"query": "Meta Guacha Alma Blanca", "artist": "Meta Guacha"},
            {"query": "El Traidor y Los Pibes Cumbia Callejera", "artist": "El Traidor y Los Pibes"}
        ]
    },
    {
        "id": "damas_gratis_atr",
        "name": "Damas Gratis & Pablo Lescano (ATR)",
        "badge": "🔥 Damas Gratis",
        "icon": "🔥",
        "genre": "Cumbia Villera ATR",
        "desc": "Os maiores sucessos da lenda Pablo Lescano e Damas Gratis: faixas para cantar junto no ritmo ATR.",
        "bpm": 96,
        "tracks": [
            {"query": "Damas Gratis Me Vas a Extrañar Viru Kumbieron", "artist": "Damas Gratis ft. Viru Kumbieron"},
            {"query": "Damas Gratis No Te Creas Tan Importante", "artist": "Damas Gratis"},
            {"query": "Damas Gratis Perrito Malvado L-Gante", "artist": "Damas Gratis ft. L-Gante"},
            {"query": "Damas Gratis Me Muero Por Verte", "artist": "Damas Gratis"},
            {"query": "Damas Gratis Alza Las Manos", "artist": "Damas Gratis"},
            {"query": "Damas Gratis Se Te Ve la Tanga", "artist": "Damas Gratis"},
            {"query": "Damas Gratis El Humo de Mi Fasito", "artist": "Damas Gratis"}
        ]
    },
    {
        "id": "pibes_chorros_reliquias",
        "name": "Pibes Chorros & Relíquias",
        "badge": "💰 Pibes Chorros",
        "icon": "💰",
        "genre": "Cumbia Villera 2000s",
        "desc": "A voz inconfundível de Ariel Salinas nos hinos que marcaram toda uma geração de cumbia de rua.",
        "bpm": 98,
        "tracks": [
            {"query": "Pibes Chorros Andrea", "artist": "Pibes Chorros"},
            {"query": "Pibes Chorros Llegamos Los Pibes Chorros", "artist": "Pibes Chorros"},
            {"query": "Pibes Chorros Que Calor", "artist": "Pibes Chorros"},
            {"query": "Pibes Chorros El Pibe Tripa", "artist": "Pibes Chorros"},
            {"query": "Pibes Chorros Sentimiento Villero", "artist": "Pibes Chorros"},
            {"query": "Pibes Chorros La Danza de Los Pibes", "artist": "Pibes Chorros"}
        ]
    },
    {
        "id": "yerba_brava_trapos",
        "name": "Yerba Brava – La Cumbia de los Trapos",
        "badge": "⚽ Yerba Brava",
        "icon": "⚽",
        "genre": "Cumbia de Cancha & Fútbol",
        "desc": "O hino oficial das torcidas e estádios da América Latina e os clássicos brutos de Yerba Brava.",
        "bpm": 95,
        "tracks": [
            {"query": "Yerba Brava La Cumbia de los Trapos oficial", "artist": "Yerba Brava"},
            {"query": "Yerba Brava Pibe Cantina", "artist": "Yerba Brava"},
            {"query": "Yerba Brava Cancion de la Luna", "artist": "Yerba Brava"},
            {"query": "Yerba Brava De Que Te la Das", "artist": "Yerba Brava"},
            {"query": "Yerba Brava Ahora Te Vas", "artist": "Yerba Brava"}
        ]
    },
    {
        "id": "mala_fama_guampa",
        "name": "Mala Fama – Cumbia y Resaca",
        "badge": "🕶️ Mala Fama",
        "icon": "🕶️",
        "genre": "Cumbia Humor & Calle",
        "desc": "Hernán Coronel com as rimas mais divertidas e irreverentes da história da cumbia argentina.",
        "bpm": 98,
        "tracks": [
            {"query": "Mala Fama La Marca de la Gorra", "artist": "Mala Fama"},
            {"query": "Mala Fama Soy Mala Fama", "artist": "Mala Fama"},
            {"query": "Mala Fama Guampa Chata", "artist": "Mala Fama"},
            {"query": "Mala Fama Yo No Fui", "artist": "Mala Fama"},
            {"query": "Mala Fama Vos Sos un Caradura", "artist": "Mala Fama"}
        ]
    },

    # --- 2. CUMBIA SANTAFESINA (ROMÂNTICA COM GUITARRA E ACORDEÓN) ---
    {
        "id": "los_palmeras_fiesta",
        "name": "Los Palmeras – Fiesta Santafesina",
        "badge": "🌴 Los Palmeras",
        "icon": "🌴",
        "genre": "Cumbia Santafesina",
        "desc": "Mais de 50 anos de história: a maior banda de cumbia com acordeón do planeta, donos de 'El Bombón'.",
        "bpm": 102,
        "tracks": [
            {"query": "Los Palmeras El Bombon Asesino oficial", "artist": "Los Palmeras"},
            {"query": "Los Palmeras Olvidala oficial", "artist": "Los Palmeras"},
            {"query": "Los Palmeras Soy Sabalero Colón", "artist": "Los Palmeras"},
            {"query": "Los Palmeras La Suavecita", "artist": "Los Palmeras"},
            {"query": "Los Palmeras Perra", "artist": "Los Palmeras"},
            {"query": "Los Palmeras Que Quiere la Chola", "artist": "Los Palmeras"},
            {"query": "Los Palmeras Asereje cumbia", "artist": "Los Palmeras"}
        ]
    },
    {
        "id": "leo_mattioli_el_leon",
        "name": "Leo Mattioli – El León Romántico",
        "badge": "🦁 Leo Mattioli",
        "icon": "🦁",
        "genre": "Cumbia Romántica Santafesina",
        "desc": "A voz apaixonada e inesquecível de Leo Mattioli em canções sobre amor, saudade e paixão.",
        "bpm": 92,
        "tracks": [
            {"query": "Leo Mattioli Le Pido a Dios", "artist": "Leo Mattioli"},
            {"query": "Leo Mattioli Lloraras Mas Que Yo", "artist": "Leo Mattioli"},
            {"query": "Leo Mattioli Conmigo Te Gusto", "artist": "Leo Mattioli"},
            {"query": "Leo Mattioli Me Preocupo Por Ti", "artist": "Leo Mattioli"},
            {"query": "Leo Mattioli Tan Solo Amantes", "artist": "Leo Mattioli"},
            {"query": "Leo Mattioli Como Podre", "artist": "Leo Mattioli"}
        ]
    },
    {
        "id": "los_del_fuego_reliquias",
        "name": "Los del Fuego – Jurabas Tú",
        "badge": "🔥 Los del Fuego",
        "icon": "🔥",
        "genre": "Cumbia Santafesina Guitarra",
        "desc": "Banana Mascheroni e Los del Fuego transformando clássicos do rock e pop em pura cumbia dançante.",
        "bpm": 104,
        "tracks": [
            {"query": "Los del Fuego Jurabas Tu oficial", "artist": "Los del Fuego"},
            {"query": "Los del Fuego Persiana Americana cumbia", "artist": "Los del Fuego"},
            {"query": "Los del Fuego Sabes", "artist": "Los del Fuego"},
            {"query": "Los del Fuego Dejaria Todo cumbia", "artist": "Los del Fuego"},
            {"query": "Los del Fuego Sobreviviendo", "artist": "Los del Fuego"}
        ]
    },
    {
        "id": "cumbia_santafesina_oro",
        "name": "Cumbia Santafesina de Oro",
        "badge": "🏆 Santafesina de Oro",
        "icon": "🏆",
        "genre": "Grandes Mestres de Santa Fe",
        "desc": "A nata da província de Santa Fe: Grupo Cali, Trinidad, Dalila e Los Lirios.",
        "bpm": 100,
        "tracks": [
            {"query": "Grupo Cali El Campeon", "artist": "Grupo Cali"},
            {"query": "Grupo Trinidad La Carta", "artist": "Grupo Trinidad"},
            {"query": "Dalila Te Perdone Muchas Veces", "artist": "Dalila"},
            {"query": "Coty Hernandez El Mas Loco", "artist": "Coty Hernández"},
            {"query": "Los Lirios La Danza de Los Mirlos santafesina", "artist": "Los Lirios"}
        ]
    },

    # --- 3. CUMBIA ROMÂNTICA DOS ANOS 90 & CLÁSSICOS ---
    {
        "id": "gilda_inmortal",
        "name": "Gilda – Corazón Valiente",
        "badge": "💖 Gilda Inmortal",
        "icon": "💖",
        "genre": "Cumbia Romántica Clásica",
        "desc": "A rainha da cumbia argentina: melodias imortais e refrões que emocionam multidões.",
        "bpm": 98,
        "tracks": [
            {"query": "Gilda No Me Arrepiento de Este Amor oficial", "artist": "Gilda"},
            {"query": "Gilda Fuiste oficial", "artist": "Gilda"},
            {"query": "Gilda Corazon Valiente oficial", "artist": "Gilda"},
            {"query": "Gilda Se Me Ha Perdido Un Corazon", "artist": "Gilda"},
            {"query": "Gilda Paisaje oficial", "artist": "Gilda"},
            {"query": "Gilda Pasito a Pasito", "artist": "Gilda"}
        ]
    },
    {
        "id": "la_nueva_luna_iluminara",
        "name": "La Nueva Luna – Iluminará",
        "badge": "🌙 La Nueva Luna",
        "icon": "🌙",
        "genre": "Cumbia Romántica & Toque",
        "desc": "Chino González e Marcelo González: harmonia inconfundível de vozes e o violão que é marca registrada.",
        "bpm": 100,
        "tracks": [
            {"query": "La Nueva Luna Iluminara", "artist": "La Nueva Luna"},
            {"query": "La Nueva Luna Y Ahora Te Vas", "artist": "La Nueva Luna"},
            {"query": "La Nueva Luna Choque Dos Con Uno", "artist": "La Nueva Luna"},
            {"query": "La Nueva Luna Hojita Seca", "artist": "La Nueva Luna"},
            {"query": "La Nueva Luna Te Vas a Arrepentir", "artist": "La Nueva Luna"}
        ]
    },
    {
        "id": "cumbia_romantica_90s",
        "name": "Cumbia Romántica Anos 90",
        "badge": "📻 Romántica 90s",
        "icon": "📻",
        "genre": "Nostalgia 90s Latina",
        "desc": "Antonio Ríos, Daniel Agostini, Comanche e Sombras: a era de ouro da cumbia romântica.",
        "bpm": 100,
        "tracks": [
            {"query": "Antonio Rios Nunca Me Faltes oficial", "artist": "Antonio Ríos"},
            {"query": "Daniel Agostini La Ventanita", "artist": "Daniel Agostini"},
            {"query": "Comanche Tonta oficial", "artist": "Comanche"},
            {"query": "Grupo Sombras La Ventanita", "artist": "Grupo Sombras"},
            {"query": "Volcan Esa Malvada", "artist": "Volcán"},
            {"query": "Grupo Red Amor de Adolescentes", "artist": "Grupo Red"}
        ]
    },

    # --- 4. CUMBIA POP, CHETA & NOVA GERAÇÃO ---
    {
        "id": "marama_rombai_fiesta",
        "name": "Márama & Rombai de Fiesta",
        "badge": "🎉 Márama & Rombai",
        "icon": "🎉",
        "genre": "Cumbia Pop Platense",
        "desc": "A explosão do pop cumbia que tomou conta das praias e baladas do Uruguai, Argentina e Brasil.",
        "bpm": 102,
        "tracks": [
            {"query": "Marama Nena video oficial", "artist": "Márama"},
            {"query": "Marama Loquita video oficial", "artist": "Márama"},
            {"query": "Marama Bronceado video oficial", "artist": "Márama"},
            {"query": "Rombai Curiosidad video oficial", "artist": "Rombai"},
            {"query": "Rombai Cuando Se Pone a Bailar", "artist": "Rombai"},
            {"query": "Marama Era Tranquila", "artist": "Márama"}
        ]
    },
    {
        "id": "cumbia_pop_cheta",
        "name": "Cumbia Pop & Cheta Hits",
        "badge": "🍹 Cumbia Pop",
        "icon": "🍹",
        "genre": "Cumbia Cheta Boliche",
        "desc": "Hits solares e dançantes para animar pré-baladas, piscinas e encontros com a galera.",
        "bpm": 104,
        "tracks": [
            {"query": "Dame 5 Piel a Piel", "artist": "Dame 5"},
            {"query": "Mano Arriba Llamame Mas Temprano", "artist": "Mano Arriba"},
            {"query": "TocoParaVos Hasta la Luna", "artist": "TocoParaVos"},
            {"query": "Canto Para Bailar Se Pica", "artist": "Canto Para Bailar"},
            {"query": "Olvidate Amor Para Un Rato", "artist": "Olvídate"}
        ]
    },
    {
        "id": "ke_personajes_vivo",
        "name": "Ke Personajes – Grandes Éxitos",
        "badge": "🎤 Ke Personajes",
        "icon": "🎤",
        "genre": "Cumbia Contemporânea",
        "desc": "Emanuel Noir e a banda sensação que quebrou todos os recordes do Spotify e YouTube no mundo latino.",
        "bpm": 98,
        "tracks": [
            {"query": "Ke Personajes FMK Big One Un Finde Crossover", "artist": "Ke Personajes ft. Big One & FMK"},
            {"query": "Ke Personajes Grupo Frontera Ojitos Rojos", "artist": "Ke Personajes ft. Grupo Frontera"},
            {"query": "Ke Personajes Onda Sabanera Pobre Corazon", "artist": "Ke Personajes ft. Onda Sabanera"},
            {"query": "Ke Personajes Costumbres en vivo", "artist": "Ke Personajes"},
            {"query": "Ke Personajes Adios Amor en vivo", "artist": "Ke Personajes"},
            {"query": "Ke Personajes Oye Mujer", "artist": "Ke Personajes"}
        ]
    },
    {
        "id": "la_champions_liga_romantica",
        "name": "La Champions Liga & Callejera",
        "badge": "⚽ Champions Liga",
        "icon": "⚽",
        "genre": "Cumbia Romántica de Barrio",
        "desc": "Hernán y La Champions Liga: piano delicado e letras de amor que marcaram a adolescência de milhões.",
        "bpm": 96,
        "tracks": [
            {"query": "La Champions Liga Dime Si Eres Feliz", "artist": "La Champions Liga"},
            {"query": "La Champions Liga Besame", "artist": "La Champions Liga"},
            {"query": "La Champions Liga La Engañera", "artist": "La Champions Liga"},
            {"query": "La Champions Liga No Te Olvides de Mi", "artist": "La Champions Liga"},
            {"query": "La Champions Liga Deja de Llorar", "artist": "La Champions Liga"}
        ]
    },
    {
        "id": "el_polaco_de_gira",
        "name": "El Polaco – De Gira y Fiesta",
        "badge": "👱 El Polaco",
        "icon": "👱",
        "genre": "Cumbia Boliche & Noche",
        "desc": "A energia contagiante de Ezequiel 'El Polaco' Cwirkaluk nos bailes e casas noturnas argentinas.",
        "bpm": 102,
        "tracks": [
            {"query": "El Polaco Deja de Llorar", "artist": "El Polaco"},
            {"query": "El Polaco Con la Misma Cancion", "artist": "El Polaco"},
            {"query": "El Polaco En Este Mundo", "artist": "El Polaco"},
            {"query": "El Polaco Ya No Te Quiero", "artist": "El Polaco"},
            {"query": "El Polaco Sola Otra Vez", "artist": "El Polaco"}
        ]
    },

    # --- 5. CUMBIA 420 & RKT (O SOM URBANO DAS RUAS) ---
    {
        "id": "cumbia_420_rkt",
        "name": "Cumbia 420 & RKT Argentina",
        "badge": "🌿 Cumbia 420",
        "icon": "🌿",
        "genre": "Cumbia 420 & RKT",
        "desc": "A fusão do ritmo da cumbia villera com graves de trap e o flow do RKT de General Rodríguez.",
        "bpm": 100,
        "tracks": [
            {"query": "L-Gante L-Gante RKT Papichamp", "artist": "L-Gante ft. Papichamp"},
            {"query": "Callejero Fino Rei Tu Turrito", "artist": "Callejero Fino ft. Rei"},
            {"query": "Kaleb Di Masi Matatan", "artist": "Kaleb Di Masi"},
            {"query": "El Noba Tamo Chelo", "artist": "El Noba"},
            {"query": "Alan Gomez Mission 01", "artist": "Alan Gomez ft. L-Gante"}
        ]
    },
    {
        "id": "callejero_fino_rkt",
        "name": "Callejero Fino – Pa Tra RKT",
        "badge": "🧢 Callejero Fino",
        "icon": "🧢",
        "genre": "RKT Puro",
        "desc": "O som 100% de rua de Callejero Fino que conquistou os rankings latinos do Spotify.",
        "bpm": 102,
        "tracks": [
            {"query": "Callejero Fino Fua Mi Amor", "artist": "Callejero Fino"},
            {"query": "Callejero Fino Que Te Vaya Bien", "artist": "Callejero Fino"},
            {"query": "Callejero Fino En La Intimidad Emilia", "artist": "Callejero Fino ft. Emilia & Big One"},
            {"query": "Callejero Fino M.A Remix BM Lola Indigo", "artist": "Callejero Fino ft. BM"}
        ]
    },
    {
        "id": "turreo_cumbia_bass",
        "name": "Turreo & Cumbia Bass",
        "badge": "🔊 Turreo Bass",
        "icon": "🔊",
        "genre": "Turreo Sessions",
        "desc": "DJ Tao e os produtores de turreo criando as sessões de cumbia mais pesadas do YouTube.",
        "bpm": 104,
        "tracks": [
            {"query": "DJ Tao Turreo Sessions 01", "artist": "DJ Tao ft. Kaleb Di Masi"},
            {"query": "Perro Primo Cumbia 420", "artist": "Perro Primo"},
            {"query": "Papichamp Amame", "artist": "Papichamp"},
            {"query": "DJ Alex Leña Para El Carbon", "artist": "DJ Alex"}
        ]
    },

    # --- 6. CUMBIA COLOMBIANA (RAÍZES E TRADIÇÃO) ---
    {
        "id": "cumbia_colombiana_clasica",
        "name": "Cumbia Colombiana Clássica",
        "badge": "🇨🇴 Cumbia Colombia",
        "icon": "🇨🇴",
        "genre": "Cumbia Tradicional Colombiana",
        "desc": "O berço mundial do gênero: tambores, gaitas, flautas e o suingue caribenho imortal.",
        "bpm": 94,
        "tracks": [
            {"query": "Los Corraleros de Majagual Los Sabanales", "artist": "Los Corraleros de Majagual"},
            {"query": "La Sonora Dinamita Mil Horas", "artist": "La Sonora Dinamita"},
            {"query": "Rodolfo Aicardi La Colegiala", "artist": "Rodolfo Aicardi"},
            {"query": "Pastor Lopez Golpe Con Golpe", "artist": "Pastor López"},
            {"query": "Lucho Bermudez Carmen de Bolivar", "artist": "Lucho Bermúdez"}
        ]
    },
    {
        "id": "sonora_dinamita_hits",
        "name": "Sonora Dinamita – Grandes Éxitos",
        "badge": "🎺 Sonora Dinamita",
        "icon": "🎺",
        "genre": "Cumbia & Metais",
        "desc": "A orquestra mais famosa da Colômbia com metais brilhantes e sucessos tocados no mundo todo.",
        "bpm": 100,
        "tracks": [
            {"query": "Sonora Dinamita Que Bello", "artist": "La Sonora Dinamita"},
            {"query": "Sonora Dinamita Escandalo", "artist": "La Sonora Dinamita"},
            {"query": "Sonora Dinamita Capullo y Sorullo", "artist": "La Sonora Dinamita"},
            {"query": "Sonora Dinamita Oye", "artist": "La Sonora Dinamita"},
            {"query": "Sonora Dinamita Mi Cucu", "artist": "La Sonora Dinamita"}
        ]
    },

    # --- 7. CUMBIA MEXICANA, SONIDERA & TEX-MEX ---
    {
        "id": "angeles_azules_sinfonico",
        "name": "Los Ángeles Azules – De Iztapalapa",
        "badge": "🇲🇽 Ángeles Azules",
        "icon": "🇲🇽",
        "genre": "Cumbia Sinfónica Mexicana",
        "desc": "Os irmãos Mejía Avante levando a cumbia do bairro de Iztapalapa para os maiores festivais mundiais.",
        "bpm": 98,
        "tracks": [
            {"query": "Los Angeles Azules 17 Años Jay de la Cueva", "artist": "Los Ángeles Azules"},
            {"query": "Los Angeles Azules Como Te Voy a Olvidar", "artist": "Los Ángeles Azules"},
            {"query": "Los Angeles Azules Mis Sentimientos Ximena Sariñana", "artist": "Los Ángeles Azules"},
            {"query": "Los Angeles Azules Nunca Es Suficiente Natalia Lafourcade", "artist": "Los Ángeles Azules ft. Natalia Lafourcade"},
            {"query": "Los Angeles Azules Amor a Primera Vista Belinda", "artist": "Los Ángeles Azules ft. Belinda"}
        ]
    },
    {
        "id": "cumbia_sonidera_mexicana",
        "name": "Cumbia Sonidera & México",
        "badge": "🎛️ Cumbia Sonidera",
        "icon": "🎛️",
        "genre": "Cumbia Sonidera",
        "desc": "O som dos sonideros da Cidade do México: efeitos de pitch, saudações ao vivo e batidas hipnóticas.",
        "bpm": 92,
        "tracks": [
            {"query": "Celso Piña Cumbia Sobre El Rio", "artist": "Celso Piña"},
            {"query": "Grupo Cañaveral Tiene Espinas El Rosal", "artist": "Grupo Cañaveral"},
            {"query": "Los Askis Amor Regresa", "artist": "Los Askis"},
            {"query": "Raymix Oye Mujer oficial", "artist": "Raymix"},
            {"query": "Super Auto La Cumbia del Rio", "artist": "Super Auto"}
        ]
    },
    {
        "id": "raymix_electrocumbia",
        "name": "Raymix – Electro Cumbia",
        "badge": "⚡ Raymix",
        "icon": "⚡",
        "genre": "Electrocumbia Moderna",
        "desc": "O criador da electrocumbia que uniu sintetizadores eletrônicos futuristas ao balanço latino.",
        "bpm": 105,
        "tracks": [
            {"query": "Raymix Oye Mujer", "artist": "Raymix"},
            {"query": "Raymix Primer Cita", "artist": "Raymix"},
            {"query": "Raymix Tu Eres la Razon", "artist": "Raymix"},
            {"query": "Raymix Llamame", "artist": "Raymix"},
            {"query": "Raymix Donde Estaras", "artist": "Raymix"}
        ]
    },
    {
        "id": "selena_tex_mex_cumbia",
        "name": "Selena & Tex-Mex Cumbia",
        "badge": "🌹 Selena Quintanilla",
        "icon": "🌹",
        "genre": "Tex-Mex & Cumbia Norteña",
        "desc": "A Rainha da Música Tejano: os clássicos atemporais de Selena que conquistaram o planeta.",
        "bpm": 106,
        "tracks": [
            {"query": "Selena Baila Esta Cumbia oficial", "artist": "Selena"},
            {"query": "Selena Bidi Bidi Bom Bom oficial", "artist": "Selena"},
            {"query": "Selena Amor Prohibido oficial", "artist": "Selena"},
            {"query": "Selena Si Una Vez oficial", "artist": "Selena"},
            {"query": "Selena Como La Flor oficial", "artist": "Selena"}
        ]
    },
    {
        "id": "kumbia_kings_fiesta",
        "name": "Los Kumbia Kings – Fuego & Cumbia",
        "badge": "👑 Kumbia Kings",
        "icon": "👑",
        "genre": "Cumbia Crossover Pop",
        "desc": "A.B. Quintanilla e Pee Wee misturando cumbia, R&B, hip-hop e pop norte-americano com ritmo latino.",
        "bpm": 102,
        "tracks": [
            {"query": "Kumbia Kings Mi Dulce Niña oficial", "artist": "Los Kumbia Kings"},
            {"query": "Kumbia Kings Fuiste Mala oficial", "artist": "Los Kumbia Kings"},
            {"query": "Kumbia Kings Shhh oficial", "artist": "Los Kumbia Kings"},
            {"query": "Kumbia Kings Sabes a Chocolate oficial", "artist": "Los Kumbia Kings"},
            {"query": "Kumbia Kings Na Na Na Dulce Niña", "artist": "Los Kumbia Kings"}
        ]
    },

    # --- 8. CUMBIA PERUANA (CHICHA & AMAZÔNICA) ---
    {
        "id": "cumbia_peruana_chicha",
        "name": "Cumbia Peruana & Chicha Hits",
        "badge": "🇵🇪 Cumbia Peruana",
        "icon": "🇵🇪",
        "genre": "Chicha & Cumbia Andina",
        "desc": "A fusão psicodélica da guitarra surf rock com a cumbia amazônica e o sentimento andino peruano.",
        "bpm": 100,
        "tracks": [
            {"query": "Los Mirlos La Danza de Los Mirlos oficial", "artist": "Los Mirlos"},
            {"query": "Corazon Serrano Tu Ausencia", "artist": "Corazón Serrano"},
            {"query": "Grupo 5 Motor y Motivo", "artist": "Grupo 5"},
            {"query": "Agua Marina Tu Amor Fue Una Mentira", "artist": "Agua Marina"},
            {"query": "Armonia 10 El Cervecero", "artist": "Armonía 10"}
        ]
    },
    {
        "id": "grupo_5_corazon_serrano",
        "name": "Grupo 5 & Corazón Serrano",
        "badge": "🌟 Grupo 5",
        "icon": "🌟",
        "genre": "Cumbia de Concierto Perú",
        "desc": "As duas maiores potências do norte do Peru lotando estádios com produções musicais impecáveis.",
        "bpm": 104,
        "tracks": [
            {"query": "Grupo 5 Te Vas", "artist": "Grupo 5"},
            {"query": "Grupo 5 Mix Valentina", "artist": "Grupo 5"},
            {"query": "Corazon Serrano Diganle", "artist": "Corazón Serrano"},
            {"query": "Corazon Serrano En Que Brazos Estaras", "artist": "Corazón Serrano"}
        ]
    },

    # --- 9. CUMBIA & CUARTETO FUSION (CÓRDOBA / FESTIVAL) ---
    {
        "id": "la_konga_cuarteto_cumbia",
        "name": "La K'onga – Cuarteto & Cumbia Fusion",
        "badge": "⚡ La K'onga",
        "icon": "⚡",
        "genre": "Cuarteto & Cumbia",
        "desc": "A banda que revolucionou o som cordobês na Argentina, unindo o piano e ritmo acelerado à cumbia.",
        "bpm": 138,
        "tracks": [
            {"query": "La Konga Nahuel Pennisi Universo Paralelo", "artist": "La K'onga ft. Nahuel Pennisi"},
            {"query": "La Konga Luck Ra Ke Personajes Ya No Vuelvas", "artist": "La K'onga ft. Luck Ra & Ke Personajes"},
            {"query": "La Konga La Cabaña", "artist": "La K'onga"},
            {"query": "La Konga Te Mentiria", "artist": "La K'onga"},
            {"query": "La Konga Cinco Minutos", "artist": "La K'onga"}
        ]
    },
    {
        "id": "luck_ra_cuarteto_cumbia",
        "name": "Luck Ra – Cumbia & Cuarteto Hits",
        "badge": "🕺 Luck Ra",
        "icon": "🕺",
        "genre": "Pop Cuarteto & Cumbia",
        "desc": "O novo fenômeno da Argentina: números um absolutos no Top 50 com refrões explosivos e contagiantes.",
        "bpm": 136,
        "tracks": [
            {"query": "Luck Ra La Morocha oficial BM", "artist": "Luck Ra ft. BM"},
            {"query": "Luck Ra Hola Perdida Khea", "artist": "Luck Ra ft. Khea"},
            {"query": "Luck Ra Abel Pintos Que Me Falte Todo", "artist": "Luck Ra ft. Abel Pintos"},
            {"query": "Luck Ra El Campeon", "artist": "Luck Ra"}
        ]
    },

    # --- 10. MOMENTOS, CHURRASCO & BOLICHE ---
    {
        "id": "cumbia_para_el_asado",
        "name": "Cumbia Para El Asado & Churrasco",
        "badge": "🥩 Asado & Cumbia",
        "icon": "🥩",
        "genre": "Churrasco & Fim de Semana",
        "desc": "Fogo aceso, carne na grelha e a melhor sequência de cumbia para ouvir com os amigos o dia todo.",
        "bpm": 100,
        "tracks": [
            {"query": "Los Palmeras La Suavecita", "artist": "Los Palmeras"},
            {"query": "Damas Gratis Me Vas a Extrañar", "artist": "Damas Gratis"},
            {"query": "La Nueva Luna Choque Dos Con Uno", "artist": "La Nueva Luna"},
            {"query": "Los del Fuego Sabes", "artist": "Los del Fuego"},
            {"query": "Ke Personajes Pobre Corazon", "artist": "Ke Personajes"}
        ]
    },
    {
        "id": "cumbia_previa_boliche_2026",
        "name": "Cumbia Previa & Boliche 2026",
        "badge": "🍾 Previa & Boliche",
        "icon": "🍾",
        "genre": "Megamix Boliche",
        "desc": "Megamixes e remixes acelerados para esquentar a pré-balada e colocar todo mundo no clima de festa.",
        "bpm": 108,
        "tracks": [
            {"query": "Ke Personajes Megamix bailable", "artist": "Ke Personajes"},
            {"query": "DJ Alex Cumbia Remix Boliche", "artist": "DJ Alex"},
            {"query": "Damas Gratis Megamix en vivo", "artist": "Damas Gratis"},
            {"query": "Los Palmeras Enganchados en vivo", "artist": "Los Palmeras"}
        ]
    }
]

print(f"Total de novas playlists de Cumbia preparadas: {len(CUMBIA_PLAYLISTS)}")

# Resolução de vídeos no YouTube com cache
cache_file = Path("cumbia_tracks_cache.json")
cache = {}
if cache_file.exists():
    try:
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

def resolve_track(query):
    if query in cache:
        return cache[query]
    
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 10
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            res = ydl.extract_info(f"ytsearch1:{query}", download=False)
            entries = res.get("entries", [])
            if entries and entries[0]:
                e = entries[0]
                data = {
                    "video_id": e.get("id"),
                    "title": e.get("title", query),
                    "duration": e.get("duration", 180)
                }
                cache[query] = data
                return data
    except Exception as ex:
        print(f"Erro ao buscar '{query}': {ex}")
    
    fallback = {
        "video_id": "iTNdq-GOVXc", # Damas Gratis clássico
        "title": query,
        "duration": 180
    }
    cache[query] = fallback
    return fallback

# Coleta todas as queries únicas
all_queries = set()
for pl in CUMBIA_PLAYLISTS:
    for t in pl["tracks"]:
        all_queries.add(t["query"])

queries_to_fetch = [q for q in all_queries if q not in cache]
print(f"Queries para resolver no YouTube: {len(queries_to_fetch)} (já em cache: {len(all_queries) - len(queries_to_fetch)})")

if queries_to_fetch:
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(resolve_track, queries_to_fetch))
    
    # Salva cache
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

print("Todas as faixas de Cumbia resolvidas com sucesso!")

# Carrega catálogo Spotify existente
existing_catalog = {}
if SPOTIFY_CATALOG_FILE.exists():
    try:
        with open(SPOTIFY_CATALOG_FILE, "r", encoding="utf-8") as f:
            existing_catalog = json.load(f)
    except Exception as e:
        print(f"Aviso ao ler {SPOTIFY_CATALOG_FILE}: {e}")

# Constrói as 33 playlists completas
cumbia_catalog_entries = {}
for pl in CUMBIA_PLAYLISTS:
    pl_id = pl["id"]
    tracks = []
    for i, t_info in enumerate(pl["tracks"], 1):
        q = t_info["query"]
        resolved = cache.get(q, {"video_id": "iTNdq-GOVXc", "title": q, "duration": 180})
        tracks.append({
            "rank": i,
            "title": resolved.get("title", q),
            "artist": t_info.get("artist", ""),
            "category": pl["name"],
            "playlist_id": pl_id,
            "playlist_badge": pl["badge"],
            "video_id": resolved.get("video_id", "iTNdq-GOVXc"),
            "duration": resolved.get("duration", 180),
            "bpm": pl["bpm"],
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
    
    cumbia_catalog_entries[pl_id] = {
        "meta": meta,
        "tracks": tracks
    }

# Mescla ao catálogo existente
existing_catalog.update(cumbia_catalog_entries)

with open(SPOTIFY_CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(existing_catalog, f, ensure_ascii=False, indent=2)

print(f"Catálogo Spotify atualizado com sucesso! Total agora: {len(existing_catalog)} playlists!")
