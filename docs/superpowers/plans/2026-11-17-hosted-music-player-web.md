# Hosted Music Player (video-only, free static hosting) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the copied project at `C:\Users\Mbello\Desktop\youtube-music-player-web` into a static site, hostable for free on Netlify, where any visitor can browse/search the existing catalog and play tracks via the official YouTube embed, with their own queue, playback history and personal "my library" additions kept per-browser — no server-side audio extraction, no OAuth, no shared mutable state.

**Architecture:** The existing `player.html` + `assets/js/player.js` stay almost untouched. Two new ES modules (`assets/js/discovery.js`, `assets/js/local-state-api.js`) load before `player.js` and transparently intercept its existing `fetch("/api/...")` calls, answering them from `localStorage` instead of a Python backend. One Netlify Function (`netlify/functions/youtube-search.mts`) is the only server-side code left, calling the official YouTube Data API v3 with a domain-restricted key, cached via Netlify Blobs to protect the shared 100-search/day quota. `engineMode` is forced to `"video"` (the iframe engine that already exists in `player.js`), so playback never depends on server-side audio extraction.

**Tech Stack:** Vanilla JS (ES modules) on the frontend, Netlify Functions (TypeScript, `.mts`) + Netlify Blobs for the search backend, Node's built-in `node:test` runner for all new code, Netlify CLI for local dev/deploy.

**Spec:** This plan implements the design approved in conversation on 2026-11-17 (no separate spec file was written — the approved design is summarized in Global Constraints below and in the task list; it covers: video-only hosted site, per-browser state, static shared catalog, one search function with cache).

## Global Constraints

- No server-side YouTube audio extraction or proxying in the hosted build — only the official iframe embed (`engineMode = "video"`, already implemented in `player.js`).
- No OAuth, no personal Google/YouTube account used by the hosted site. Search uses a YouTube Data API v3 key, restricted by HTTP referrer to the deployed domain.
- Shared/global state in this build: the catalog (`window.DATA`, `window.CATEGORIES`, `window.ICONS`, `window.SPOTIFY_PLAYLISTS`, baked into `player.html` at build time) is read-only for all visitors.
- Per-visitor state (queue, playback history, personal library additions, genre rotation index, seen-suggestion ids) lives in that browser's `localStorage` only — never sent to or merged on a server.
- `search.list` costs 100 quota units per call against a 10,000/day free quota (~100 calls/day shared across every visitor and every feature that searches). `youtube-search.mts` must cache by normalized query via Netlify Blobs to stretch this budget, and every caller must degrade gracefully (empty results, not a crash) when the quota is exhausted.
- `discoverRelatedTracks` (the Python original issues up to ~7 queries per call) is capped at 2 queries in this port — a deliberate trade of recall for quota budget, since this runs automatically, not just on explicit user search.
- Duration-based filtering (Python's `dur < 40 or dur > 2400` exclusion) is dropped in v1: `search.list` doesn't return duration, and a second `videos.list` call per result to get it is extra quota spend for a non-essential filter. Documented simplification, not an oversight.
- Only files the approved design named are removed from the copy: `igtoyt/`, `apply_*.py`, `fix_*.py`, `test_*.py`/`test_*.bat`, `tests/`, `saved_audios_all.json`, `processed*.json`, `playback_history.json`. Everything else in the copy is left alone even if unused — no speculative cleanup.
- `player.js` (9,696 lines) is not edited for the `/api/*` call sites. All interception happens by patching `window.fetch`, specifically to keep this a low-risk, reviewable change instead of ~25 scattered edits.

## Review Focus

- **YouTube quota exhausted:** `youtube-search.mts` returns an error from the YouTube API (403/quota) — must come back as `{ tracks: [], quotaExceeded: true }`, not throw, and every caller (search, discover, related) must still render whatever local-catalog/cached results it has instead of breaking the UI.
- **Embed-disabled or removed video during playback:** confirmed `player.js` already wires `onDeckError` on both YT.Player decks (player.js:7758, 7782) — Task 8 only needs to verify this still skips to the next track in "video" mode; it must not be reimplemented.
- **`localStorage` unavailable** (Safari private mode, cookies/storage blocked): every read/write in `local-state-api.js` and `discovery.js` must be wrapped so a thrown `localStorage` access falls back to an in-memory store for that page load, rather than breaking the whole page.
- **First-time visitor, every key empty:** queue, history, personal library, seen-ids and rotation-index reads must all default to empty/zero without `null`/`undefined` errors, including when merging the (empty) personal library into `window.DATA`.
- **Duplicate add across a reload:** adding the same `video_id` to the queue or to the personal library twice (e.g., revisiting a page, a double click) must not create duplicate entries — mirrors the existing dedupe-by-`video_id` behavior in the Python original.

---

### Task 1: Remove the approved-for-deletion files from the copy

**Files:**
- Delete: `igtoyt/` (entire directory)
- Delete: `apply_drop_hunter_and_title_fix.py`, `apply_full_stems_hud_and_transition_fixes.py`, `apply_full_transition_and_vocal_zero_bleed_fix.py`, `apply_multi_genre_zero_bleed_stems.py`, `apply_quad_fixes.py`, `apply_stems_pro_engine.py`, `apply_studio_suite.py`, `apply_upgrades.py`, `apply_variable_drop_and_hud_expansion.py`
- Delete: `fix_premature_cuts_and_mix_jumper.py`, `fix_preset_cards_layout.py`
- Delete: every `test_*.py` and `test_*.bat` file at the project root
- Delete: `tests/` (entire directory, including `tests/__pycache__`)
- Delete: `saved_audios_all.json`, `processed.json`, `processed_categorized.json`, `playback_history.json`
- Delete: `conftest.py` (only used by the deleted `tests/`)

**Interfaces:** None — this task only removes files nothing else in this plan reads.

- [ ] **Step 1: Delete the directories and files listed above**

Use the filesystem directly (this is a cleanup task, not logic — no test to write first).

- [ ] **Step 2: Verify nothing still references the deleted paths**

Run: `grep -rn "igtoyt\|saved_audios_all\|playback_history.json" player.html assets/ *.py 2>/dev/null`
Expected: no output (or only matches inside files that are themselves being deleted/already gone).

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: remove Instagram-pipeline and local-dev-only files from the hosted copy"
```

---

### Task 2: Node/Netlify project scaffolding

**Files:**
- Create: `package.json`
- Create: `netlify.toml`
- Modify: `.gitignore`

**Interfaces:**
- Produces: a Node ESM project (`"type": "module"`) that `npm test` (→ `node --test`) and `npm install` both succeed in, and that Netlify recognizes as a static site with `publish = "."` and `functions = "netlify/functions"`. Later tasks' functions and modules assume this.

- [ ] **Step 1: Write `package.json`**

`"type": "module"`, `"scripts": { "test": "node --test" }`, dependencies `@netlify/functions` and `@netlify/blobs`, devDependency `netlify-cli`.

- [ ] **Step 2: Write `netlify.toml`**

```toml
[build]
  publish = "."
  functions = "netlify/functions"
```

- [ ] **Step 3: Add to `.gitignore`**

Append `node_modules/`, `.netlify/`, `cookies.txt` (defense in depth — it's already absent from this copy, but must never be re-added).

- [ ] **Step 4: Install and verify**

Run: `npm install && npm test`
Expected: install succeeds; `node --test` reports 0 tests, 0 failures (no test files exist yet).

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json netlify.toml .gitignore
git commit -m "chore: scaffold Node/Netlify project for the hosted build"
```

---

### Task 3: YouTube search function with caching

**Files:**
- Create: `netlify/functions/youtube-search.mts`
- Test: `netlify/functions/youtube-search.test.mts`

**Interfaces:**
- Produces: `export async function searchYouTube({ query, limit, apiKey, fetchImpl, blobStore }): Promise<{ tracks: Array<{ video_id: string, title: string, artist: string }>, quotaExceeded?: boolean }>` — the pure, dependency-injected core, imported directly by tests and by this file's own default handler.
- Produces: `export default` Netlify function handler at `config.path = "/api/youtube-search"`, calling `searchYouTube` with `Netlify.env.get("YOUTUBE_API_KEY")`, the real `fetch`, and `getStore("youtube-search-cache")` from `@netlify/blobs`.
- Consumes (Task 4/5/6 will call this): `GET /api/youtube-search?q=<query>&limit=<n>` returning the same JSON shape as `searchYouTube`'s resolved value.

- [ ] **Step 1: Write the failing test for a cache miss**

```ts
test("searchYouTube calls the YouTube API and caches the result", async () => {
  const fetchCalls = [];
  const fetchImpl = async (url) => { fetchCalls.push(url); return new Response(JSON.stringify({
    items: [{ id: { videoId: "abc123" }, snippet: { title: "Song Title", channelTitle: "Some Channel" } }]
  }), { status: 200 }); };
  const store = new Map();
  const blobStore = { get: async (k) => store.get(k) ?? null, setJSON: async (k, v) => store.set(k, v) };

  const result = await searchYouTube({ query: "mega funk 2024", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.equal(fetchCalls.length, 1);
  assert.ok(fetchCalls[0].includes("key=FAKE_KEY"));
  assert.deepEqual(result.tracks, [{ video_id: "abc123", title: "Song Title", artist: "Some Channel" }]);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test netlify/functions/youtube-search.test.mts`
Expected: FAIL — `searchYouTube` not defined / module not found.

- [ ] **Step 3: Implement `searchYouTube` in `netlify/functions/youtube-search.mts`**

Call `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=<limit>&q=<query>&key=<apiKey>` via `fetchImpl`. Map `items[].id.videoId` → `video_id`, `items[].snippet.title` → `title`, `items[].snippet.channelTitle` → `artist`. On a non-2xx response, return `{ tracks: [], quotaExceeded: true }` instead of throwing (Review Focus item 1).

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test netlify/functions/youtube-search.test.mts`
Expected: PASS

- [ ] **Step 5: Write the failing test for a cache hit (no second network call)**

```ts
test("searchYouTube returns the cached result on a repeat query without calling fetch again", async () => {
  let fetchCallCount = 0;
  const fetchImpl = async () => { fetchCallCount++; return new Response(JSON.stringify({
    items: [{ id: { videoId: "abc123" }, snippet: { title: "Song Title", channelTitle: "Some Channel" } }]
  }), { status: 200 }); };
  const store = new Map();
  const blobStore = { get: async (k) => store.get(k) ?? null, setJSON: async (k, v) => store.set(k, v) };

  await searchYouTube({ query: "Mega Funk 2024", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });
  const second = await searchYouTube({ query: "mega funk 2024  ", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.equal(fetchCallCount, 1);
  assert.equal(second.tracks[0].video_id, "abc123");
});
```

- [ ] **Step 6: Run test to verify it fails**

Run: `node --test netlify/functions/youtube-search.test.mts`
Expected: FAIL — second call still hits `fetchImpl` (no caching yet).

- [ ] **Step 7: Implement caching in `searchYouTube`**

Cache key = normalized query (trim + lowercase) + limit. Before calling the API, check `blobStore.get(key)`; if present, return it. After a successful API call, `blobStore.setJSON(key, result)`. No TTL field is tracked yet — Netlify Blobs entries are cheap and the catalog of queries is small and repetitive (genre rotation queries, popular searches), so an indefinite cache is acceptable here; note this as the deliberate choice (not a gap) if revisited later.

- [ ] **Step 8: Run test to verify it passes**

Run: `node --test netlify/functions/youtube-search.test.mts`
Expected: PASS (both tests)

- [ ] **Step 9: Write the default handler (no test — thin glue, exercised in Task 9's manual smoke test)**

```ts
export default async (req: Request) => {
  const url = new URL(req.url);
  const query = url.searchParams.get("q") || "";
  const limit = Number(url.searchParams.get("limit")) || 15;
  const result = await searchYouTube({
    query, limit,
    apiKey: Netlify.env.get("YOUTUBE_API_KEY") || "",
    fetchImpl: fetch,
    blobStore: getStore("youtube-search-cache"),
  });
  return Response.json(result);
};
export const config = { path: "/api/youtube-search" };
```

- [ ] **Step 10: Commit**

```bash
git add netlify/functions/youtube-search.mts netlify/functions/youtube-search.test.mts
git commit -m "feat: add cached YouTube search function"
```

---

### Task 4: Discovery module — BPM estimation and category resolution

**Files:**
- Create: `assets/js/discovery.js`
- Test: `assets/js/discovery.test.mjs`

**Interfaces:**
- Produces: `export const GENRE_BPM_RANGES` (object, same 10 keys/values as `server.py`'s `GENRE_BPM_RANGES`).
- Produces: `export const GENRE_SEARCH_QUERIES` (object, same 10 keys/query-lists as `server.py`'s `GENRE_SEARCH_QUERIES`).
- Produces: `export function detectOrEstimateBpm(title: string, category: string): number`.
- Produces: `export function resolveOfficialCategory(title: string, artist?: string): string`.
- Produces: `export const OFFICIAL_CATEGORIES` (array, same 10 entries as `server.py`'s `OFFICIAL_CATEGORIES`).

- [ ] **Step 1: Write the failing tests for `detectOrEstimateBpm`**

```js
test("detectOrEstimateBpm reads an explicit BPM from the title", () => {
  assert.equal(detectOrEstimateBpm("Ritmada Pesada 135 BPM", "Outros"), 135);
});

test("detectOrEstimateBpm falls back to a deterministic in-range estimate", () => {
  const first = detectOrEstimateBpm("Some Track Title", "Sertanejo Antigo & Modão");
  const second = detectOrEstimateBpm("Some Track Title", "Sertanejo Antigo & Modão");
  assert.equal(first, second); // deterministic
  assert.ok(first >= 80 && first <= 110); // within that category's range
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `node --test assets/js/discovery.test.mjs`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement `GENRE_BPM_RANGES`, `GENRE_SEARCH_QUERIES`, `OFFICIAL_CATEGORIES`, `detectOrEstimateBpm` in `assets/js/discovery.js`**

Port the values verbatim from `server.py` lines 96-230 and 506-517. For the fallback estimate, use any deterministic string hash (does not need to bit-match Python's `md5` — only needs to be stable for the same input) modulo the category's `(high - low + 1)`, offset by `low`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `node --test assets/js/discovery.test.mjs`
Expected: PASS

- [ ] **Step 5: Write the failing tests for `resolveOfficialCategory`**

```js
test("resolveOfficialCategory matches funk keywords", () => {
  assert.equal(resolveOfficialCategory("MC Fulano - Montagem Pesada", ""), "Funk Paulista, BH & Mandelão");
});

test("resolveOfficialCategory falls back to Outros", () => {
  assert.equal(resolveOfficialCategory("Completely Unrelated Title", "Unknown Artist"), "Outros");
});
```

- [ ] **Step 6: Run tests to verify they fail, then implement, then verify they pass**

Port the regex ladder verbatim from `server.py:519-537`.

- [ ] **Step 7: Commit**

```bash
git add assets/js/discovery.js assets/js/discovery.test.mjs
git commit -m "feat: port BPM estimation and category resolution to JS"
```

---

### Task 5: Discovery module — genre rotation and track discovery

**Files:**
- Modify: `assets/js/discovery.js`
- Modify: `assets/js/discovery.test.mjs`

**Interfaces:**
- Consumes: `GENRE_SEARCH_QUERIES`, `detectOrEstimateBpm`, `GENRE_BPM_RANGES` from Task 4 (same file).
- Produces: `export function getNextQuery(category: string, storage: Storage): string` — `Storage` means any object with `getItem(key): string|null` and `setItem(key, value)`.
- Produces: `export function collectExcludedIds({ libraryData, queue, seenIds }): Set<string>`.
- Produces: `export async function discoverTracks({ category, customQuery, seedBpm, limit, storage, libraryData, queue, searchFn }): Promise<Array<Track>>` where `Track = { video_id, title, artist, category, bpm, query_used? }` and `searchFn: (query: string, limit: number) => Promise<{ tracks: Array<{video_id,title,artist}> }>`.
- Produces: `export async function discoverRelatedTracks({ title, artist, category, currentVideoId, targetBpm, limit, storage, libraryData, queue, searchFn }): Promise<Array<Track>>` — issues **at most 2** queries to `searchFn` (Global Constraints).

- [ ] **Step 1: Write the failing test for `getNextQuery`**

```js
test("getNextQuery rotates through the category's query list and persists the index", () => {
  const storage = fakeStorage();
  const queries = GENRE_SEARCH_QUERIES["Samba & Pagode"];
  assert.equal(getNextQuery("Samba & Pagode", storage), queries[0]);
  assert.equal(getNextQuery("Samba & Pagode", storage), queries[1]);
});
```

Define a small `fakeStorage()` helper at the top of the test file (an object backed by a plain `Map`, implementing `getItem`/`setItem`).

- [ ] **Step 2: Run, fail, implement, run, pass**

Port `get_next_query` from `server.py:276-293`: read a JSON object from `storage.getItem("genre_rotation")` (default `{}`), use/increment the per-category index mod `queries.length`, write it back.

- [ ] **Step 3: Write the failing test for `collectExcludedIds`**

```js
test("collectExcludedIds unions library, queue and seen ids", () => {
  const ids = collectExcludedIds({
    libraryData: { "Outros": [{ video_id: "lib1" }] },
    queue: [{ video_id: "q1" }],
    seenIds: ["seen1"],
  });
  assert.deepEqual([...ids].sort(), ["lib1", "q1", "seen1"]);
});
```

- [ ] **Step 4: Run, fail, implement, run, pass**

- [ ] **Step 5: Write the failing test for `discoverTracks`**

```js
test("discoverTracks excludes known ids and sorts by closeness to the seed BPM", async () => {
  const storage = fakeStorage();
  const searchFn = async () => ({ tracks: [
    { video_id: "known", title: "Already have 130 BPM", artist: "" },
    { video_id: "far", title: "Far Track 90 BPM", artist: "" },
    { video_id: "close", title: "Close Track 128 BPM", artist: "" },
  ] });
  const results = await discoverTracks({
    category: "Mega Funk & Ritmadas", seedBpm: 130, limit: 10, storage,
    libraryData: { "Outros": [{ video_id: "known" }] }, queue: [], searchFn,
  });
  assert.deepEqual(results.map(t => t.video_id), ["close", "far"]); // "known" excluded, closest first
});
```

- [ ] **Step 6: Run, fail, implement, run, pass**

Port `discover_tracks` from `server.py:296-376`, minus the duration filter (Global Constraints) and using `searchFn` instead of a direct network call. Mark returned ids as seen by writing the union into `storage.setItem("seen_suggested_ids", ...)` (only when `customQuery` is falsy, matching the Python original's behavior).

- [ ] **Step 7: Write the failing test for `discoverRelatedTracks`'s query cap**

```js
test("discoverRelatedTracks issues at most 2 searches", async () => {
  const storage = fakeStorage();
  let callCount = 0;
  const searchFn = async () => { callCount++; return { tracks: [] }; };
  await discoverRelatedTracks({
    title: "Some Song", artist: "Some Artist", category: "Mega Funk & Ritmadas",
    currentVideoId: "cur1", targetBpm: 130, limit: 10, storage,
    libraryData: {}, queue: [], searchFn,
  });
  assert.ok(callCount <= 2);
});
```

- [ ] **Step 8: Run, fail, implement, run, pass**

Port `discover_related_tracks` from `server.py:379-502`: clean title/artist, build the energy-aware query list the same way, but only consume the first 2 queries from it. Keep the title-keyword exclusion filter and the BPM-closeness sort.

- [ ] **Step 9: Commit**

```bash
git add assets/js/discovery.js assets/js/discovery.test.mjs
git commit -m "feat: port genre rotation and track discovery to JS, capped for quota"
```

---

### Task 6: Local-state API — queue, history, library, search (fetch interceptor core)

**Files:**
- Create: `assets/js/local-state-api.js`
- Test: `assets/js/local-state-api.test.mjs`

**Interfaces:**
- Consumes: `discoverTracks`, `discoverRelatedTracks`, `resolveOfficialCategory`, `OFFICIAL_CATEGORIES` from `assets/js/discovery.js` (Tasks 4-5).
- Produces (all storage-injected, `storage: Storage` as in Task 5): `getQueue(storage)`, `addToQueue(storage, track)`, `removeFromQueue(storage, videoId)`, `clearQueue(storage)`, `getHistory(storage)`, `addToHistory(storage, track)`, `clearHistory(storage)`, `addToLibrary(storage, libraryData, track)`, `removeFromLibrary(storage, libraryData, videoId)`, `moveInLibrary(storage, libraryData, videoId, newCategory, oldCategory)`, `buildWatchVideosUrl(queue)`.
- Produces: `export function createInterceptedFetch({ originalFetch, storage, getLibraryData, searchFnForYoutube }): (input, init) => Promise<Response>` — the router, matching the paths/methods below and falling back to `originalFetch` for everything else. For `/api/suggestions/discover` and `/api/suggestions/related`, the router supplies `storage`, `libraryData: getLibraryData()`, `queue: getQueue(storage)` and `searchFn: searchFnForYoutube` to `discoverTracks`/`discoverRelatedTracks` (Task 5) — it does not duplicate their logic, only gathers their arguments.
- Produces (used only at module load, not unit-tested — see Task 7): a default export object `{ installOnWindow() }` that wires `window.fetch`.

Response shapes to match exactly (copied from `server.py`, read in full for this plan):
- `GET /api/queue` → bare array.
- `POST /api/queue/add` (body `{video_id,title,artist,category}`) → `{success:true, count, queue}`.
- `POST /api/queue/remove` (body `{video_id}`) → `{success:true, count, queue}`.
- `POST /api/queue/clear` → `{success:true, count:0, queue:[]}`.
- `GET /api/history` → `{history:[...]}`.
- `POST /api/history/add` (body `{track}`) → `{status:"ok", count}`; skip insert if `history[0].video_id === track.video_id` (server.py:959); cap at 200 entries; fill `track.category` via `resolveOfficialCategory` if missing/invalid, same as `server.py:960-962`.
- `POST /api/history/clear` → `{status:"cleared", count:0}`.
- `POST /api/library/add` (body `{video_id,title,artist,category,source}`) → `{success:true, video_id, title, category, count}`; dedupe by `video_id`; resolve category via `resolveOfficialCategory` if missing/invalid (server.py:988-989).
- `POST /api/library/remove` (body `{video_id,category}`) → `{success:true, removed_count, video_id, count}`.
- `POST /api/library/move` (body `{video_id,new_category,old_category}`) → `{success, video_id, new_category, count}`.
- `POST /api/suggestions/discover` (body `{category,title,bpm,query}`) → `{success:true, category, tracks, count}`, calling `discoverTracks`.
- `GET or POST /api/suggestions/related` → `{success:true, title, artist, category, target_bpm, tracks, count}`, calling `discoverRelatedTracks`.
- `POST /api/suggestions/reset-seen` → `{success:true, message}`; clears the seen-ids storage key.
- `GET or POST /api/search` (query/body `q`/`query`, `category`) → `{tracks, library_tracks, youtube_tracks, count}`: `library_tracks` = substring match (accent-insensitive, same as `server.py:553-565`) over the flattened `getLibraryData()`; `youtube_tracks` = `searchFnForYoutube(query, limit)` result, tagged with `resolveOfficialCategory` where missing, `in_library` computed against the library match set — same merge as `server.py:539-590`.
- `POST /api/sync-youtube` → `{success:true, message, queue_count, playlist_url}` where `playlist_url = buildWatchVideosUrl(queue)` (no network call — this mirrors `server.py:1122-1141`'s URL but skips the OAuth-pipeline background sync, which is out of scope).

- [ ] **Step 1: Write the failing tests for queue functions**

```js
test("addToQueue appends a new track and is idempotent on the same video_id", () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "A", category: "Outros" });
  addToQueue(storage, { video_id: "v1", title: "T", artist: "A", category: "Outros" });
  assert.equal(getQueue(storage).length, 1);
});

test("removeFromQueue filters by video_id", () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "A", category: "Outros" });
  removeFromQueue(storage, "v1");
  assert.deepEqual(getQueue(storage), []);
});
```

- [ ] **Step 2: Run, fail, implement `getQueue`/`addToQueue`/`removeFromQueue`/`clearQueue`, run, pass**

Add and cover one more case while here (Review Focus item 4): `getQueue` on completely empty storage returns `[]`, not `null`/throw.

- [ ] **Step 3: Write the failing tests for history functions**

```js
test("addToHistory skips a consecutive duplicate of the same video_id", () => {
  const storage = fakeStorage();
  addToHistory(storage, { video_id: "v1", title: "T" });
  addToHistory(storage, { video_id: "v1", title: "T" });
  assert.equal(getHistory(storage).length, 1);
});

test("addToHistory caps at 200 entries", () => {
  const storage = fakeStorage();
  for (let i = 0; i < 205; i++) addToHistory(storage, { video_id: `v${i}`, title: "T" });
  assert.equal(getHistory(storage).length, 200);
});
```

- [ ] **Step 4: Run, fail, implement, run, pass**

- [ ] **Step 5: Write the failing tests for library functions**

```js
test("addToLibrary is idempotent by video_id and resolves a missing category", () => {
  const storage = fakeStorage();
  const libraryData = {};
  const result = addToLibrary(storage, libraryData, { video_id: "v1", title: "Montagem Pesada MC Fulano", artist: "" });
  assert.equal(result.category, "Funk Paulista, BH & Mandelão");
  addToLibrary(storage, libraryData, { video_id: "v1", title: "Montagem Pesada MC Fulano", artist: "" });
  assert.equal(result.count, 1); // second add is a no-op, count unchanged
});

test("moveInLibrary changes the category of an existing entry", () => {
  const storage = fakeStorage();
  const libraryData = {};
  addToLibrary(storage, libraryData, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  moveInLibrary(storage, libraryData, "v1", "Samba & Pagode", "Outros");
  assert.equal(getPersonalLibrary(storage)[0].category, "Samba & Pagode");
});
```

(`getPersonalLibrary(storage)` is the storage-reading half of what Task 7 merges into `window.DATA`; expose it here since this task owns the storage shape.)

- [ ] **Step 6: Run, fail, implement `addToLibrary`/`removeFromLibrary`/`moveInLibrary`/`getPersonalLibrary`, run, pass**

- [ ] **Step 7: Write the failing test for `buildWatchVideosUrl`**

```js
test("buildWatchVideosUrl joins video ids into a watch_videos URL", () => {
  const url = buildWatchVideosUrl([{ video_id: "a" }, { video_id: "b" }]);
  assert.equal(url, "https://www.youtube.com/watch_videos?video_ids=a,b");
});
```

- [ ] **Step 8: Run, fail, implement, run, pass**

- [ ] **Step 9: Write the failing test for the search merge**

```js
test("createInterceptedFetch /api/search merges library matches and YouTube results", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({
    originalFetch: async () => { throw new Error("should not hit network for /api/search"); },
    storage,
    getLibraryData: () => ({ "Outros": [{ video_id: "lib1", title: "Funk Clássico", artist: "", category: "Outros" }] }),
    searchFnForYoutube: async () => ({ tracks: [{ video_id: "yt1", title: "Funk Novo", artist: "Channel" }] }),
  });
  const res = await fetchFn("/api/search?q=funk");
  const data = await res.json();
  assert.equal(data.library_tracks.length, 1);
  assert.equal(data.youtube_tracks.length, 1);
  assert.equal(data.count, 2);
});
```

- [ ] **Step 10: Run, fail, implement `createInterceptedFetch`'s `/api/search` branch and the overall router skeleton (default: call `originalFetch`), run, pass**

- [ ] **Step 11: Write the failing tests for the remaining routed paths**

One assertion per path, each checking only the response shape against the list above (queue/history/library already unit-tested directly in Steps 1-6; here the test is that the router dispatches to them correctly, e.g.:

```js
test("createInterceptedFetch routes POST /api/queue/add to addToQueue", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/queue/add", { method: "POST", body: JSON.stringify({ video_id: "v1", title: "T", artist: "", category: "Outros" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.queue.length, 1);
});
```

Repeat the pattern for `/api/queue/remove`, `/api/queue/clear`, `GET /api/queue`, `GET /api/history`, `/api/history/add`, `/api/history/clear`, `/api/library/add`, `/api/library/remove`, `/api/library/move`, `/api/suggestions/discover`, `/api/suggestions/related`, `/api/suggestions/reset-seen`, `/api/sync-youtube`.

- [ ] **Step 12: Run, fail, implement the rest of the router, run, pass (all tests)**

- [ ] **Step 13: Write the failing test for quota-exceeded degradation (Review Focus item 1)**

```js
test("/api/search still returns library matches when the YouTube search is quota-exceeded", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({
    originalFetch: async () => { throw new Error("no network"); }, storage,
    getLibraryData: () => ({ "Outros": [{ video_id: "lib1", title: "Funk Clássico", artist: "", category: "Outros" }] }),
    searchFnForYoutube: async () => ({ tracks: [], quotaExceeded: true }),
  });
  const res = await fetchFn("/api/search?q=funk");
  const data = await res.json();
  assert.equal(data.library_tracks.length, 1);
  assert.equal(data.tracks.length, 1); // doesn't crash, doesn't lose the library match
});
```

- [ ] **Step 14: Run, fail (if it already passes, the merge logic from Step 10 already handles it — confirm, don't skip), implement if needed, run, pass**

- [ ] **Step 15: Write the failing test for `localStorage` throwing (Review Focus item 3)**

```js
test("getQueue falls back to an empty list when storage.getItem throws", () => {
  const storage = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };
  assert.deepEqual(getQueue(storage), []);
});
```

- [ ] **Step 16: Run, fail, wrap every storage access in this file in try/catch with an empty/default fallback, run, pass**

- [ ] **Step 17: Commit**

```bash
git add assets/js/local-state-api.js assets/js/local-state-api.test.mjs
git commit -m "feat: add localStorage-backed fetch interceptor for queue/history/library/search"
```

---

### Task 7: Library/DATA merge on load and engine-mode lockdown

**Files:**
- Modify: `assets/js/local-state-api.js`
- Modify: `assets/js/local-state-api.test.mjs`

**Interfaces:**
- Consumes: `getPersonalLibrary(storage)` from Task 6 (same file).
- Produces: `export function mergePersonalLibraryIntoData(DATA, storage): void` — mutates `DATA` in place, prepending personal entries into their category arrays, idempotent across repeated calls.
- Produces: `export function lockEngineModeToVideo(storage): void` — `storage.setItem("pref_engine_mode", "video")`.
- Produces: a bottom-of-file side-effecting block (not unit-tested, see Task 8) that, when `typeof window !== "undefined"`, calls `lockEngineModeToVideo(window.localStorage)`, `mergePersonalLibraryIntoData(window.DATA, window.localStorage)`, and installs the intercepted fetch from Task 6 onto `window.fetch`.

- [ ] **Step 1: Write the failing test for the merge**

```js
test("mergePersonalLibraryIntoData adds personal tracks without duplicating on a second call", () => {
  const storage = fakeStorage();
  addToLibrary(storage, {}, { video_id: "v1", title: "T", artist: "", category: "Samba & Pagode" });
  const DATA = { "Samba & Pagode": [{ video_id: "existing" }] };
  mergePersonalLibraryIntoData(DATA, storage);
  mergePersonalLibraryIntoData(DATA, storage); // second call, same storage
  assert.equal(DATA["Samba & Pagode"].filter(t => t.video_id === "v1").length, 1);
  assert.equal(DATA["Samba & Pagode"].some(t => t.video_id === "existing"), true);
});

test("mergePersonalLibraryIntoData creates the category array if DATA doesn't have it yet", () => {
  const storage = fakeStorage();
  addToLibrary(storage, {}, { video_id: "v1", title: "T", artist: "", category: "Trap & Rap Nacional" });
  const DATA = {};
  mergePersonalLibraryIntoData(DATA, storage);
  assert.equal(DATA["Trap & Rap Nacional"].length, 1);
});

test("mergePersonalLibraryIntoData on a first-time visitor (empty storage) leaves DATA untouched and does not throw", () => {
  const storage = fakeStorage();
  const DATA = { "Outros": [{ video_id: "existing" }] };
  mergePersonalLibraryIntoData(DATA, storage);
  assert.deepEqual(DATA, { "Outros": [{ video_id: "existing" }] });
});
```

- [ ] **Step 2: Run, fail, implement, run, pass**

- [ ] **Step 3: Write the failing test for `lockEngineModeToVideo`**

```js
test("lockEngineModeToVideo always sets the stored preference to video", () => {
  const storage = fakeStorage();
  storage.setItem("pref_engine_mode", "audio");
  lockEngineModeToVideo(storage);
  assert.equal(storage.getItem("pref_engine_mode"), "video");
});
```

- [ ] **Step 4: Run, fail, implement, run, pass**

- [ ] **Step 5: Add the bottom-of-file bootstrap block (no test — thin glue, verified visually in Task 8/9)**

- [ ] **Step 6: Commit**

```bash
git add assets/js/local-state-api.js assets/js/local-state-api.test.mjs
git commit -m "feat: merge personal library into DATA on load and lock hosted build to video engine mode"
```

---

### Task 8: Wire the new scripts into `player.html`, hide the audio-mode toggle

**Files:**
- Modify: `player.html:8` (stylesheet link), `player.html:1230-1236` (script tags)
- Modify: `assets/css/player.css` (one new rule)

**Interfaces:**
- Consumes: `assets/js/discovery.js`, `assets/js/local-state-api.js` (Tasks 4-7) as `<script type="module">` tags.

- [ ] **Step 1: Add the CSS rule hiding the engine-mode toggle**

Append to `assets/css/player.css`: `#barEngineModeBtn { display: none !important; }`

- [ ] **Step 2: Insert the two new script tags in `player.html`**

Right after the existing inline `<script>window.DATA = ...; window.SPOTIFY_PLAYLISTS = ...;</script>` block (around line 1233) and before the `iframe_api`/`player.js` script tags (lines 1235-1236), add:

```html
<script type="module" src="/assets/js/discovery.js?v=hosted1"></script>
<script type="module" src="/assets/js/local-state-api.js?v=hosted1"></script>
```

- [ ] **Step 3: Verify by reading the file**

Confirm the final tag order is: inline `window.DATA=...` script → `discovery.js` → `local-state-api.js` → `iframe_api` → `player.js`. `local-state-api.js` must run its merge/lockdown before `player.js`'s top-level `const DATA = window.DATA || {}` (player.js:3) executes — module scripts execute in document order before any subsequent classic script, so this ordering is sufficient; no `defer`/`async` needed and none should be added.

- [ ] **Step 4: Confirm `onDeckError` still skips to the next track (Review Focus item 2 — verification only, no code change)**

Run: `grep -n "function onDeckError" -A 15 assets/js/player.js`
Expected: the function advances playback (e.g. calls whatever "play next" function the rest of the file uses) rather than leaving the player stuck. If it does not, stop and flag this to the user — do not patch `player.js` as part of this plan.

- [ ] **Step 5: Commit**

```bash
git add player.html assets/css/player.css
git commit -m "feat: load the hosted-state scripts and hide the audio-engine toggle"
```

---

### Task 9: Local end-to-end smoke test with `netlify dev`

**Files:** None created or modified — this task only runs and observes the app.

- [ ] **Step 1: Set a placeholder `YOUTUBE_API_KEY`**

Run: `netlify env:set YOUTUBE_API_KEY <a-real-or-throwaway-key> --local` (or export it in the shell `netlify dev` runs in). A real key is needed to see actual search results; without one, confirm instead that the UI degrades per Review Focus item 1 rather than crashing.

- [ ] **Step 2: Start the dev server**

Run: `netlify dev`
Expected: serves `player.html` at the printed local URL, with `netlify/functions/youtube-search.mts` available at `/api/youtube-search`.

- [ ] **Step 3: Manually exercise the app in a browser and confirm:**
  - The "🎵 Áudio HD" button is not visible anywhere in the bar.
  - Playback happens through the YouTube embed (video visible), not silently failing.
  - Searching a track returns results; adding one to the queue and reloading the page keeps it in the queue.
  - Adding a track to "Minha Biblioteca" and reloading shows it under its category.
  - Clearing the browser's `localStorage` for the site and reloading shows an empty queue/history/library with no console errors (Review Focus item 4).
  - Repeating all of the above in a private/incognito window with storage blocked does not crash the page (Review Focus item 3) — a degraded, no-persistence experience is acceptable; a blank/broken page is not.

- [ ] **Step 4: Fix anything found, re-run the affected unit tests, then re-verify manually**

- [ ] **Step 5: Commit any fixes from this task**

```bash
git add -A
git commit -m "fix: address issues found in local netlify dev smoke test"
```

(Skip this step if Step 3 found nothing to fix.)

---

### Task 10: Deploy to Netlify

**Files:** None in the repo — this is account/infrastructure setup plus a deploy.

- [ ] **Step 1: Create a restricted YouTube Data API v3 key**

In the existing Google Cloud project (the one `client_secret.json` belonged to, or a new one), create an API key, restrict it to the YouTube Data API v3, and add an HTTP referrer restriction for the Netlify domain once it's known (Step 3 gives you the domain; come back and add the restriction right after).

- [ ] **Step 2: Create the Netlify site and set the environment variable**

Run: `netlify init` (or link an existing site), then `netlify env:set YOUTUBE_API_KEY <the-real-key>` with the Functions scope included.

- [ ] **Step 3: Deploy via CLI, not a git-connected build**

Run: `netlify deploy --prod`
(Per the user's own prior experience, a git-connected Netlify build can be blocked by a `Co-Authored-By` trailer in commit messages misread as the cause of a private-repo error — deploying by CLI from the local folder avoids that path entirely.)

- [ ] **Step 4: Add the HTTP referrer restriction from Step 1 now that the live domain is known**

- [ ] **Step 5: Re-run the Task 9 manual checklist against the live URL**

Expected: same results as local, now over the real deployed domain and the real, referrer-restricted API key.

- [ ] **Step 6: Tell the user the live URL**

No commit — this task only touches external account configuration.
