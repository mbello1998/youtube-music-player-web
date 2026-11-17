import { discoverTracks, discoverRelatedTracks, resolveOfficialCategory, OFFICIAL_CATEGORIES } from "./discovery.js";

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

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

// --- Queue ---

export function getQueue(storage) {
  return readJSON(storage, "queue", []);
}

export function addToQueue(storage, track) {
  const queue = getQueue(storage);
  if (!queue.some((t) => t.video_id === track.video_id)) {
    queue.push(track);
    writeJSON(storage, "queue", queue);
  }
  return queue;
}

export function removeFromQueue(storage, videoId) {
  const queue = getQueue(storage).filter((t) => t.video_id !== videoId);
  writeJSON(storage, "queue", queue);
  return queue;
}

export function clearQueue(storage) {
  writeJSON(storage, "queue", []);
  return [];
}

// --- History ---

const HISTORY_LIMIT = 200;

export function getHistory(storage) {
  return readJSON(storage, "history", []);
}

export function addToHistory(storage, track) {
  const history = getHistory(storage);
  if (!history.length || history[0].video_id !== track.video_id) {
    const entry = { ...track };
    if (!entry.category || !OFFICIAL_CATEGORIES.includes(entry.category)) {
      entry.category = resolveOfficialCategory(entry.title, entry.artist);
    }
    history.unshift(entry);
    writeJSON(storage, "history", history.slice(0, HISTORY_LIMIT));
  }
  return getHistory(storage);
}

export function clearHistory(storage) {
  writeJSON(storage, "history", []);
  return [];
}

// --- Library ---

export function getPersonalLibrary(storage) {
  return readJSON(storage, "personal_library", []);
}

export function addToLibrary(storage, libraryData, track) {
  const lib = getPersonalLibrary(storage);
  const existing = lib.find((t) => t.video_id === track.video_id);
  if (!existing) {
    let category = track.category;
    if (!category || !OFFICIAL_CATEGORIES.includes(category)) {
      category = resolveOfficialCategory(track.title, track.artist);
    }
    const entry = {
      video_id: track.video_id,
      title: track.title,
      artist: track.artist || "",
      category,
      source: track.source || "Sugestões (Favoritada)",
    };
    lib.unshift(entry);
    writeJSON(storage, "personal_library", lib);
    return { video_id: entry.video_id, title: entry.title, category: entry.category, count: lib.length };
  }
  return { video_id: existing.video_id, title: existing.title, category: existing.category, count: lib.length };
}

function isInSharedCatalog(libraryData, videoId) {
  return Object.values(libraryData || {}).some((tracks) => (tracks || []).some((t) => t.video_id === videoId));
}

export function removeFromLibrary(storage, libraryData, videoId) {
  const lib = getPersonalLibrary(storage);
  const initialLen = lib.length;
  const filtered = lib.filter((t) => t.video_id !== videoId);
  writeJSON(storage, "personal_library", filtered);

  let removedCount = initialLen - filtered.length;
  // Not a personal addition — if it's one of the shared, read-only catalog
  // tracks, remember to hide it for this visitor instead of reporting a
  // false "removed" that undoes itself on the next reload.
  if (removedCount === 0 && isInSharedCatalog(libraryData, videoId)) {
    const hidden = readJSON(storage, "hidden_ids", []);
    if (!hidden.includes(videoId)) {
      hidden.push(videoId);
      writeJSON(storage, "hidden_ids", hidden);
    }
    removedCount = 1;
  }
  return { removed_count: removedCount, video_id: videoId, count: filtered.length };
}

export function moveInLibrary(storage, libraryData, videoId, newCategory, oldCategory) {
  const lib = getPersonalLibrary(storage);
  let moved = false;
  for (const t of lib) {
    if (t.video_id === videoId && (!oldCategory || t.category === oldCategory)) {
      t.category = newCategory;
      moved = true;
      break;
    }
  }
  if (!moved) {
    for (const t of lib) {
      if (t.video_id === videoId) {
        t.category = newCategory;
        moved = true;
        break;
      }
    }
  }
  writeJSON(storage, "personal_library", lib);

  // Same as removeFromLibrary: a shared-catalog track isn't in personal_library
  // at all, so record a per-visitor category override instead of a no-op.
  if (!moved && isInSharedCatalog(libraryData, videoId)) {
    const overrides = readJSON(storage, "category_overrides", {});
    overrides[videoId] = newCategory;
    writeJSON(storage, "category_overrides", overrides);
    moved = true;
  }

  return { success: moved, video_id: videoId, new_category: newCategory, count: lib.length };
}

// --- Sync URL ---

export function buildWatchVideosUrl(queue) {
  const ids = (queue || []).map((t) => t.video_id).filter(Boolean);
  if (!ids.length) return "https://www.youtube.com";
  return `https://www.youtube.com/watch_videos?video_ids=${ids.join(",")}`;
}

// --- Router ---

function stripAccents(s) {
  return String(s)
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase();
}

function searchLibrary(libraryData, query) {
  if (!query) return [];
  const qWords = stripAccents(query).split(/\s+/).filter(Boolean);
  const matches = [];
  for (const tracks of Object.values(libraryData || {})) {
    for (const t of tracks || []) {
      const haystack = stripAccents(`${t.title || ""} ${t.artist || ""} ${t.category || ""} ${t.bpm || ""}`);
      if (qWords.every((w) => haystack.includes(w))) {
        matches.push({ ...t, in_library: true });
        if (matches.length >= 50) return matches;
      }
    }
  }
  return matches;
}

async function readBody(init) {
  if (!init || !init.body) return {};
  try {
    return JSON.parse(init.body);
  } catch {
    return {};
  }
}

export function createInterceptedFetch({ originalFetch, storage, getLibraryData, searchFnForYoutube }) {
  return async function interceptedFetch(input, init) {
    const rawUrl = typeof input === "string" ? input : input.url;
    const url = new URL(rawUrl, "http://localhost");
    const path = url.pathname;
    const method = (init && init.method) || "GET";
    const params = url.searchParams;

    if (path === "/api/queue" && method === "GET") {
      return jsonResponse(getQueue(storage));
    }
    if (path === "/api/queue/add" && method === "POST") {
      const body = await readBody(init);
      const queue = addToQueue(storage, {
        video_id: body.video_id,
        title: body.title,
        artist: body.artist || "",
        category: body.category || "Outros",
      });
      return jsonResponse({ success: true, count: queue.length, queue });
    }
    if (path === "/api/queue/remove" && method === "POST") {
      const body = await readBody(init);
      const queue = removeFromQueue(storage, body.video_id);
      return jsonResponse({ success: true, count: queue.length, queue });
    }
    if (path === "/api/queue/clear" && method === "POST") {
      const queue = clearQueue(storage);
      return jsonResponse({ success: true, count: 0, queue });
    }

    if (path === "/api/history" && method === "GET") {
      return jsonResponse({ history: getHistory(storage) });
    }
    if (path === "/api/history/add" && method === "POST") {
      const body = await readBody(init);
      const history = addToHistory(storage, body.track);
      return jsonResponse({ status: "ok", count: history.length });
    }
    if (path === "/api/history/clear" && method === "POST") {
      clearHistory(storage);
      return jsonResponse({ status: "cleared", count: 0 });
    }

    if (path === "/api/library/add" && method === "POST") {
      const body = await readBody(init);
      const result = addToLibrary(storage, getLibraryData(), body);
      return jsonResponse({ success: true, ...result });
    }
    if (path === "/api/library/remove" && method === "POST") {
      const body = await readBody(init);
      const result = removeFromLibrary(storage, getLibraryData(), body.video_id);
      return jsonResponse({ success: true, ...result });
    }
    if (path === "/api/library/move" && method === "POST") {
      const body = await readBody(init);
      const result = moveInLibrary(storage, getLibraryData(), body.video_id, body.new_category, body.old_category);
      return jsonResponse(result);
    }

    if (path === "/api/suggestions/discover" && method === "POST") {
      const body = await readBody(init);
      const category = body.category || "Mega Funk & Ritmadas";
      const tracks = await discoverTracks({
        category,
        customQuery: body.query,
        seedBpm: body.bpm,
        storage,
        libraryData: getLibraryData(),
        queue: getQueue(storage),
        searchFn: searchFnForYoutube,
      });
      return jsonResponse({ success: true, category, tracks, count: tracks.length });
    }
    if (path === "/api/suggestions/related") {
      const body = method === "POST" ? await readBody(init) : {};
      const title = params.get("title") || body.title || "";
      const artist = params.get("artist") || body.artist || "";
      const category = params.get("category") || body.category || "Outros";
      const currentVideoId = params.get("video_id") || body.video_id;
      const bpmRaw = params.get("bpm") || body.bpm;
      const targetBpm = bpmRaw ? Number(bpmRaw) : undefined;
      const tracks = await discoverRelatedTracks({
        title,
        artist,
        category,
        currentVideoId,
        targetBpm,
        storage,
        libraryData: getLibraryData(),
        queue: getQueue(storage),
        searchFn: searchFnForYoutube,
      });
      return jsonResponse({ success: true, title, artist, category, target_bpm: targetBpm, tracks, count: tracks.length });
    }
    if (path === "/api/suggestions/reset-seen" && method === "POST") {
      try {
        storage.removeItem("seen_suggested_ids");
      } catch {
        // storage unavailable — nothing to reset
      }
      return jsonResponse({ success: true, message: "Histórico de sugestões resetado com sucesso." });
    }

    if (path === "/api/sync-youtube" && method === "POST") {
      const queue = getQueue(storage);
      return jsonResponse({
        success: true,
        message: "Fila convertida em link de reprodução do YouTube.",
        queue_count: queue.length,
        playlist_url: buildWatchVideosUrl(queue),
      });
    }

    if (path === "/api/search") {
      const body = method === "POST" ? await readBody(init) : {};
      const query = (params.get("q") || params.get("query") || body.q || body.query || "").trim();
      const libraryData = getLibraryData();
      const libraryTracks = searchLibrary(libraryData, query);
      const libVids = new Set(libraryTracks.map((t) => t.video_id));

      let ytTracks = [];
      if (query) {
        const ytResult = await searchFnForYoutube(query, 15);
        ytTracks = (ytResult.tracks || []).map((t) => ({
          ...t,
          category: t.category && OFFICIAL_CATEGORIES.includes(t.category) ? t.category : resolveOfficialCategory(t.title, t.artist),
          in_library: libVids.has(t.video_id),
        }));
      }

      const combined = [...libraryTracks];
      for (const yt of ytTracks) {
        if (!combined.some((c) => c.video_id === yt.video_id)) combined.push(yt);
      }

      return jsonResponse({
        tracks: combined,
        library_tracks: libraryTracks,
        youtube_tracks: ytTracks.filter((t) => !t.in_library),
        count: combined.length,
      });
    }

    return originalFetch(input, init);
  };
}

export function mergePersonalLibraryIntoData(DATA, storage) {
  const personal = getPersonalLibrary(storage);
  for (const entry of personal) {
    if (!DATA[entry.category]) DATA[entry.category] = [];
    if (!DATA[entry.category].some((t) => t.video_id === entry.video_id)) {
      DATA[entry.category].unshift(entry);
    }
  }

  const hidden = new Set(readJSON(storage, "hidden_ids", []));
  const overrides = readJSON(storage, "category_overrides", {});
  if (!hidden.size && !Object.keys(overrides).length) return;

  for (const category of Object.keys(DATA)) {
    DATA[category] = DATA[category].filter((t) => !hidden.has(t.video_id));
  }

  for (const [videoId, newCategory] of Object.entries(overrides)) {
    let moved = null;
    for (const category of Object.keys(DATA)) {
      const idx = DATA[category].findIndex((t) => t.video_id === videoId);
      if (idx !== -1) {
        [moved] = DATA[category].splice(idx, 1);
        break;
      }
    }
    if (moved) {
      moved.category = newCategory;
      if (!DATA[newCategory]) DATA[newCategory] = [];
      if (!DATA[newCategory].some((t) => t.video_id === videoId)) {
        DATA[newCategory].unshift(moved);
      }
    }
  }
}

export function lockEngineModeToVideo(storage) {
  // Raw string, not JSON — player.js reads this key directly as plain text
  // (`localStorage.getItem("pref_engine_mode") || "audio"`), not via JSON.parse.
  try {
    storage.setItem("pref_engine_mode", "video");
  } catch {
    // storage unavailable — nothing to lock, player.js's own default is "audio"
    // but the CSS hides the toggle regardless (Task 8)
  }
}

export async function fetchYouTubeSearch(query, limit) {
  try {
    const res = await fetch(`/api/youtube-search?q=${encodeURIComponent(query)}&limit=${limit}`);
    if (!res.ok) return { tracks: [], quotaExceeded: true };
    return await res.json();
  } catch {
    // network error, cold start timeout, or a non-JSON error page — degrade, never throw
    return { tracks: [], quotaExceeded: true };
  }
}

export function createMemoryStorage() {
  const map = new Map();
  return {
    getItem: (k) => (map.has(k) ? map.get(k) : null),
    setItem: (k, v) => {
      map.set(k, String(v));
    },
    removeItem: (k) => {
      map.delete(k);
    },
  };
}

// Private/incognito mode (Safari in particular) can make *accessing*
// `window.localStorage` itself throw, not just its methods — so this probes
// before ever handing the storage object to the rest of the module.
export function resolveStorage(win) {
  try {
    const s = win.localStorage;
    const probeKey = "__ymp_storage_probe__";
    s.setItem(probeKey, "1");
    s.removeItem ? s.removeItem(probeKey) : s.setItem(probeKey, "");
    return s;
  } catch {
    return createMemoryStorage();
  }
}

// Bootstrap: runs automatically when this module is loaded in a browser.
// Must execute before player.js's own top-level `const DATA = window.DATA || {}`
// (player.js:3) — the script tag order in player.html (Task 8) guarantees that.
if (typeof window !== "undefined") {
  const storage = resolveStorage(window);
  lockEngineModeToVideo(storage);
  mergePersonalLibraryIntoData(window.DATA || (window.DATA = {}), storage);
  window.fetch = createInterceptedFetch({
    originalFetch: window.fetch.bind(window),
    storage,
    getLibraryData: () => window.DATA || {},
    searchFnForYoutube: fetchYouTubeSearch,
  });
}
