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

function readJSON(storage, key, fallback) {
  try {
    const raw = storage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return parsed ?? fallback;
  } catch {
    return fallback;
  }
}

function writeJSON(storage, key, value) {
  try {
    storage.setItem(key, JSON.stringify(value));
  } catch {
    // storage unavailable (private mode etc.) — silently skip persistence
  }
}

export function getNextQuery(category, storage) {
  const queries = GENRE_SEARCH_QUERIES[category] || GENRE_SEARCH_QUERIES.Outros;
  const rotation = readJSON(storage, "genre_rotation", {});
  const currIdx = rotation[category] || 0;
  const query = queries[currIdx % queries.length];
  rotation[category] = currIdx + 1;
  writeJSON(storage, "genre_rotation", rotation);
  return query;
}

export function collectExcludedIds({ libraryData, queue, seenIds }) {
  const ids = new Set();
  Object.values(libraryData || {}).forEach((tracks) => {
    (tracks || []).forEach((t) => {
      if (t.video_id) ids.add(t.video_id);
    });
  });
  (queue || []).forEach((t) => {
    if (t.video_id) ids.add(t.video_id);
  });
  (seenIds || []).forEach((id) => ids.add(id));
  return ids;
}

export async function discoverTracks({
  category,
  customQuery,
  seedBpm,
  limit = 12,
  storage,
  libraryData,
  queue,
  searchFn,
}) {
  const seenIds = customQuery ? [] : readJSON(storage, "seen_suggested_ids", []);
  const excludedIds = customQuery
    ? new Set()
    : collectExcludedIds({ libraryData, queue, seenIds });

  const query = customQuery || getNextQuery(category, storage);
  const { tracks: rawTracks } = await searchFn(query, 25);

  const results = [];
  for (const t of rawTracks) {
    if (!t.video_id || !t.title) continue;
    if (excludedIds.has(t.video_id)) continue;
    if (results.some((r) => r.video_id === t.video_id)) continue;

    results.push({
      video_id: t.video_id,
      title: t.title,
      artist: t.artist || "",
      category,
      bpm: detectOrEstimateBpm(t.title, category),
      query_used: query,
    });
    if (results.length >= limit) break;
  }

  if (!customQuery) {
    const newIds = results.map((r) => r.video_id);
    writeJSON(storage, "seen_suggested_ids", [...new Set([...seenIds, ...newIds])]);
  }

  const [, , defaultBpm] = GENRE_BPM_RANGES[category] || [115, 130, 124];
  const targetBpm = seedBpm || defaultBpm;
  results.sort((a, b) => Math.abs(a.bpm - targetBpm) - Math.abs(b.bpm - targetBpm));

  return results;
}

const STOP_WORDS = new Set([
  "de", "da", "do", "das", "dos", "e", "em", "um", "uma", "a", "o", "as", "os", "ao", "na", "no",
  "com", "por", "para", "remix", "feat", "ft", "mc", "dj", "official", "video", "clipe",
]);

function cleanTrackText(text) {
  return (text || "")
    .replace(/\(.*?\)|\[.*?\]|feat\..*|ft\..*|clipe oficial|v[íi]deo oficial|official video|lyric video/gi, "")
    .trim();
}

export async function discoverRelatedTracks({
  title,
  artist,
  category,
  currentVideoId,
  targetBpm,
  limit = 12,
  storage,
  libraryData,
  queue,
  searchFn,
}) {
  const cleanTitle = cleanTrackText(title);
  const cleanArtist = (artist || "").replace(/\(.*?\)|\[.*?\]/g, "").trim();

  const seenIds = readJSON(storage, "seen_suggested_ids", []);
  const excludedIds = collectExcludedIds({ libraryData, queue, seenIds });
  if (currentVideoId) excludedIds.add(currentVideoId);

  const seedBpm = targetBpm || detectOrEstimateBpm(cleanTitle || title, category);

  const rawWords = (cleanTitle.toLowerCase().match(/[a-zà-ÿ0-9]{3,}/gi) || []);
  const titleKeywords = rawWords.filter((w) => !STOP_WORDS.has(w));

  const isHighEnergy =
    seedBpm >= 125 || /mega|funk|eletr|desande|trap|ritm|treino/i.test(category || "");

  const queries = [];
  if (isHighEnergy) {
    queries.push(
      `${category} treino pesado motivacao ${seedBpm} bpm`,
      `musica para treino academia pump ${seedBpm} bpm`,
      `cardio ${seedBpm} bpm bass boost treino`,
      `set treino musculacao ${category} ${seedBpm} bpm som pesado`,
      `${category} ${seedBpm} bpm lancamento`,
    );
  } else {
    queries.push(
      `${category} ${seedBpm} bpm lancamento`,
      `ritmo ${category} ${seedBpm} bpm`,
      `set ${category} ${seedBpm} bpm`,
      `novidades ${category} ${seedBpm} bpm hits 2024`,
    );
  }

  const genreList = GENRE_SEARCH_QUERIES[category] || [];
  if (genreList.length) {
    const shuffled = [...genreList].sort(() => Math.random() - 0.5);
    queries.push(...shuffled.slice(0, 2));
  }

  if (cleanArtist) {
    if (isHighEnergy) {
      queries.unshift(`${cleanArtist} treino motivacao ritmo ${seedBpm} bpm`);
      queries.push(`artistas parecidos com ${cleanArtist} ${seedBpm} bpm treino`);
    } else {
      queries.unshift(`artistas parecidos com ${cleanArtist} ${seedBpm} bpm`);
      queries.push(`${cleanArtist} ritmo ${category} ${seedBpm} bpm`);
    }
  }

  // Quota guard: the Python original issues up to ~7 queries per call; this
  // runs automatically (not just on explicit search), so it's capped at 2
  // to protect the shared YouTube search quota (see plan's Global Constraints).
  const queriesToRun = queries.slice(0, 2);

  const results = [];
  for (const q of queriesToRun) {
    if (results.length >= limit) break;
    const { tracks: rawTracks } = await searchFn(q, 15);
    for (const t of rawTracks) {
      if (results.length >= limit) break;
      if (!t.video_id || !t.title) continue;
      if (excludedIds.has(t.video_id)) continue;
      if (results.some((r) => r.video_id === t.video_id)) continue;

      const lowerTitle = t.title.toLowerCase();
      if (titleKeywords.slice(0, 2).some((kw) => lowerTitle.includes(kw))) continue;

      const bpm = detectOrEstimateBpm(t.title, category);
      results.push({
        video_id: t.video_id,
        title: t.title,
        artist: t.artist || "",
        category: category || "Relacionadas",
        bpm,
        source: `Spotify AI • ${bpm} BPM`,
      });
    }
  }

  const newIds = results.map((r) => r.video_id);
  writeJSON(storage, "seen_suggested_ids", [...new Set([...seenIds, ...newIds])]);

  results.sort((a, b) => Math.abs(a.bpm - seedBpm) - Math.abs(b.bpm - seedBpm));

  return results;
}
