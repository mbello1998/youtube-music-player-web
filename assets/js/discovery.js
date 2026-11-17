export const GENRE_BPM_RANGES = {
  "Mega Funk & Ritmadas": [130, 150, 138],
  "Funk Paulista, BH & Mandelão": [128, 140, 130],
  "Eletrônica, House & Desande": [124, 128, 126],
  "Sertanejo Universitário & Atual": [110, 130, 118],
  "Sertanejo Antigo & Modão": [80, 110, 95],
  "Reggaeton, Cachengue & Latino": [90, 105, 96],
  "Samba & Pagode": [90, 115, 102],
  "Trap & Rap Nacional": [120, 145, 135],
  "Rock & Pop Nostalgia": [110, 135, 122],
  Outros: [115, 130, 124],
};

export const OFFICIAL_CATEGORIES = [
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
];

export const GENRE_SEARCH_QUERIES = {
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
    "Ritmada montagem funk",
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
    "Set de funk bh 2024",
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
    "Slap house remix hits",
  ],
  "Sertanejo Universitário & Atual": [
    "Sertanejo universitario 2024 lancamento",
    "Henrique e Juliano novidades sertanejo",
    "Hugo e Guilherme novidades",
    "Sertanejo atual modao acustico",
    "Sertanejo balada festa 2024",
    "Zé Neto e Cristiano novidades",
    "Jorge e Mateus novidades",
    "Luan Santana hits sertanejo 2024",
  ],
  "Sertanejo Antigo & Modão": [
    "Modao sertanejo classico raiz",
    "Tiao Carreiro e Pardinho modao",
    "Milionario e Jose Rico modao bruto",
    "Chitãozinho e Xororó classicos",
    "Sertanejo raiz moda de viola",
    "Trio Parada Dura modao",
    "Geziel e Gabriel modao",
    "Modao bruto de fazenda",
  ],
  "Reggaeton, Cachengue & Latino": [
    "Reggaeton 2024 novidades latino",
    "Cachengue remix fiesta latina",
    "Bad Bunny Feid reggaeton hits",
    "Urbano latino perreo remix",
    "Plan B Wisin Yandel reggaeton classico",
    "Reggaeton bailable fiesta",
    "Cumbia cachengue argentina remix",
    "Dembow latino 2024",
  ],
  "Samba & Pagode": [
    "Pagode 2024 lancamento novidades",
    "Pagode Menos e Mais churrasco",
    "Ferrugem Dilsinho pagode atual",
    "Samba de raiz roda de samba",
    "Turma do Pagode novidades",
    "Grupo Revelacao Sorriso Maroto",
    "Pagode ao vivo churrasco balada",
    "Thiaguinho pagode hits",
  ],
  "Trap & Rap Nacional": [
    "Trap nacional 2024 lancamento",
    "Matue Teto WIU novidades trap",
    "KayBlack Veigh trap novidades",
    "Rap nacional underground",
    "Trap funk ritmado",
    "Filipe Ret L7NNON trap",
    "Cabelinho trap novidades",
    "Trap beat pesado Brasil",
  ],
  "Rock & Pop Nostalgia": [
    "Pop 2000 nostalgia hits",
    "Rock nacional anos 2000",
    "Charlie Brown Jr CPM 22 classicos",
    "Pop rock internacional flashback",
    "Indie pop rock nostalgia",
    "Nacional anos 90 e 2000",
    "Rock pop 2000 flashback hits",
  ],
  Outros: [
    "Top musicas mais tocadas Brasil 2024",
    "Hits virais do momento Brasil",
    "Remix dancante novidades 2024",
    "Músicas em alta Brasil",
    "Supermix novidades musicais",
  ],
};

function stableStringHash(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
  }
  return hash;
}

export function detectOrEstimateBpm(title, category = "Outros") {
  if (!title) return 120;

  const explicit = title.match(/\b(1[0-9]{2}|[7-9][0-9])\s*bpm\b/i);
  if (explicit) {
    const val = parseInt(explicit[1], 10);
    if (val >= 60 && val <= 200) return val;
  }

  const [low, high] = GENRE_BPM_RANGES[category] || [115, 130, 124];
  const offset = stableStringHash(title) % (high - low + 1);
  return low + offset;
}

export function resolveOfficialCategory(title, artist = "") {
  const text = `${title || ""} ${artist || ""}`.toLowerCase();

  if (/cumbia|villera|santafesina|charanga|chicha|cuarteto|reggaeton|latino|dembow|perreo|bachata|sonido profesional|fiestero|cachengue|el reja/.test(text)) {
    return "Reggaeton, Cachengue & Latino";
  }
  if (/megafunk|mega funk|ritmada|eletrofunk|eletro funk/.test(text)) {
    return "Mega Funk & Ritmadas";
  }
  if (/funk|mandel|bh|fluxo|favela|kondzilla|gr6|mc |montagem/.test(text)) {
    return "Funk Paulista, BH & Mandelão";
  }
  if (/eletr|house|desande|edm|techno|trance|psy|rave|alok|vintage/.test(text)) {
    return "Eletrônica, House & Desande";
  }
  if (/sertanejo|universit|agronejo|modao|modão|gusttavo|jorge|marilia|zeneto/.test(text)) {
    return "Sertanejo Universitário & Atual";
  }
  if (/samba|pagode|ferrugem|dilsinho|sorriso maroto|turma do pagode/.test(text)) {
    return "Samba & Pagode";
  }
  if (/trap|rap|drill|hip hop|hip-hop|matue|kayblack|veigh|filipe ret/.test(text)) {
    return "Trap & Rap Nacional";
  }
  if (/rock|pop|nostalgia|anos 80|anos 90|anos 2000/.test(text)) {
    return "Rock & Pop Nostalgia";
  }
  return "Outros";
}
