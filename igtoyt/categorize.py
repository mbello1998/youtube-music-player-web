import re
from typing import Optional

CATEGORIES = [
    "Eletrônica",
    "Sertanejo & Forró",
    "Funk & Mega Funk",
    "Trap & Rap",
    "Reggaeton & Latino",
    "Rock & Pop",
    "Outros"
]

GENRE_RULES = [
    (
        "Eletrônica",
        [
            "dom dolla", "solomun", "skepta", "illusionize", "fezzo", "topic", "a7s",
            "vintage culture", "shapeless", "astrohertz", "m83", "mochakk", "argy",
            "omnya", "silver panda", "vini vici", "blazy", "desande", "psk beat",
            "fest car", "alok", "dubdogz", "cat dealers", "boris brejcha", "fisher",
            "techno", "house", "remix", "project x", "omar svenson", "canzi.project"
        ]
    ),
    (
        "Sertanejo & Forró",
        [
            "murilo huff", "danilo e davi", "júnior e cézar", "junior e cezar",
            "joão gustavo e murilo", "grelo", "estação fandangueira", "humberto & ronaldo",
            "ícaro e gilmar", "icaro e gilmar", "george henrique & rodrigo",
            "banda primeira dama", "grupo bailaço", "garotos de ouro", "fandangueira",
            "neto e jr", "joão neto & frederico", "bruno & marrone", "guilherme & benuto",
            "milionário & josé rico", "léo magalhães", "diego & victor hugo",
            "henrique & juliano", "matheus & kauan", "felipe e rodrigo",
            "joão bosco e gabriel", "jorge & mateus", "elino julião", "zé vaqueiro",
            "andrade downloads", "fernando junior", "bagunçar minha mente",
            "máquina do tempo (forró)", "forró", "forro", "fandangueiro", "gaúcho",
            "gaucho", "sertanejo", "modão", "modao", "piseiro", "arrocha"
        ]
    ),
    (
        "Funk & Mega Funk",
        [
            "mc ryan sp", "mc meno k", "dj japa nk", "mc gp", "mc lele jp", "boladin 211",
            "dj will tn", "mc prr felipinho", "dj 7w", "dj leilton", "dj dédda", "mc kitinho",
            "mc w1", "dj felipe santos", "mc leley", "mc ld da baixada", "mc mazinho rs",
            "mc paiva zs", "dj ak beats", "dj martinelli", "dj japão", "missiatto",
            "yuri redicopa", "mc marlon ph", "dj r15", "mc torugo", "dj gu", "mc joãozinho vt",
            "mc vine7", "mc jvila", "mc marks", "mc dkziin", "mc pedrin hg", "aaron modesto",
            "mc magal", "dj glenner", "tomas", "sanchezz dj", "dj thiago pr", "jhow",
            "mc makauli", "gp da zl", "waltin", "kotim", "mc piedro", "mc negão original",
            "os gemeos da putaria", "mc pânico", "mc lorin", "wl trem bala", "mc guizinho niazi",
            "dj yuri pedrada", "mc j9", "dj guh mix", "mc don juan", "menor richard",
            "mc alan jr", "mc ig", "mc vitin lc", "dj lv mdp", "dj ph da serra",
            "dj ronaldo o brabo", "mc buret", "mc kalzin", "dj guilherme borges",
            "dj brizy", "dj teh", "mc nito", "dj vinibeats", "mc levin", "dj maloka original",
            "mc skin", "mc code", "mc mr. bim", "mc jacaré", "mc rodrigo do cn",
            "dj gouveia", "dj deivão", "menor teteu", "dj serpinha", "dj j2", "theuzzo",
            "dj jr no beat", "dj oreia", "mc tuto", "dj souza", "dj qrz", "mc th",
            "dj brenno paixão", "viidra", "dj neeh", "mc cria", "dj kn de vila velha",
            "mc vinny", "mc brinquedo", "fala na cara", "mclan", "mc lan", "corleone",
            "mc du red", "danilo no beat", "mega funk", "mandelão", "mtg", "ritmada",
            "baile", "mega mexicana", "beat berimbau", "novinha safadinha"
        ]
    ),
    (
        "Trap & Rap",
        [
            "matuê", "matue", "kyan", "mu540", "tasha & tracie", "djonga", "coyote beatz",
            "traplaudo", "mc ph", "wc no beat", "pk", "mc cabelinho", "hariel", "orochi",
            "borges", "wiu", "pedro lotto", "wey", "puterrier", "mainstreet", "heavy baile",
            "chefin", "trap", "rap", "hip hop", "r&b"
        ]
    ),
    (
        "Reggaeton & Latino",
        [
            "sonido profesional", "el chaco pa", "lira", "nico conca", "soy tu sol",
            "sonido cristal", "nicky jam", "sasha belén", "myke towers", "plan b",
            "ñengo flow", "bad bunny", "meta guacha", "callejero fino", "bm",
            "el gran combo", "chris jedi", "anuel aa", "chencho corleone", "cosculluela",
            "brytiago", "justin quiles", "feid", "atl jacob", "cumbia", "salsa", "bachata",
            "reggaeton", "latino", "urbano"
        ]
    ),
    (
        "Rock & Pop",
        [
            "nickelback", "linkin park", "party tyme karaoke", "coldplay", "phil collins",
            "paulo sergio", "seu cuca", "armandinho", "mary j. blige", "lykke li",
            "petrus.wav", "mc morena", "covers by david", "rock", "pop"
        ]
    )
]


def categorize_song(title: str, artist: str) -> str:
    combined = f"{title or ''} {artist or ''}".lower()
    for genre, keywords in GENRE_RULES:
        for kw in keywords:
            if kw in combined:
                return genre
    return "Outros"
