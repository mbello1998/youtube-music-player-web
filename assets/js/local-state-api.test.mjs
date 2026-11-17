import { test } from "node:test";
import assert from "node:assert/strict";
import {
  getQueue,
  addToQueue,
  removeFromQueue,
  clearQueue,
  getHistory,
  addToHistory,
  clearHistory,
  addToLibrary,
  removeFromLibrary,
  moveInLibrary,
  getPersonalLibrary,
  buildWatchVideosUrl,
  createInterceptedFetch,
} from "./local-state-api.js";

function fakeStorage() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => {
      map.set(key, value);
    },
    removeItem: (key) => {
      map.delete(key);
    },
  };
}

// --- Queue ---

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

test("getQueue on completely empty storage returns []", () => {
  const storage = fakeStorage();
  assert.deepEqual(getQueue(storage), []);
});

// --- History ---

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

// --- Library ---

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

// --- Sync URL ---

test("buildWatchVideosUrl joins video ids into a watch_videos URL", () => {
  const url = buildWatchVideosUrl([{ video_id: "a" }, { video_id: "b" }]);
  assert.equal(url, "https://www.youtube.com/watch_videos?video_ids=a,b");
});

// --- Router: /api/search merge ---

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

// --- Router: remaining paths ---

test("createInterceptedFetch routes POST /api/queue/add to addToQueue", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/queue/add", { method: "POST", body: JSON.stringify({ video_id: "v1", title: "T", artist: "", category: "Outros" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.queue.length, 1);
});

test("createInterceptedFetch routes POST /api/queue/remove to removeFromQueue", async () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/queue/remove", { method: "POST", body: JSON.stringify({ video_id: "v1" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.queue.length, 0);
});

test("createInterceptedFetch routes POST /api/queue/clear to clearQueue", async () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/queue/clear", { method: "POST" });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.deepEqual(data.queue, []);
});

test("createInterceptedFetch routes GET /api/queue to a bare array", async () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/queue");
  const data = await res.json();
  assert.equal(Array.isArray(data), true);
  assert.equal(data.length, 1);
});

test("createInterceptedFetch routes GET /api/history to {history}", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/history");
  const data = await res.json();
  assert.deepEqual(data, { history: [] });
});

test("createInterceptedFetch routes POST /api/history/add to addToHistory", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/history/add", { method: "POST", body: JSON.stringify({ track: { video_id: "v1", title: "T" } }) });
  const data = await res.json();
  assert.deepEqual(data, { status: "ok", count: 1 });
});

test("createInterceptedFetch routes POST /api/history/clear to clearHistory", async () => {
  const storage = fakeStorage();
  addToHistory(storage, { video_id: "v1", title: "T" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/history/clear", { method: "POST" });
  const data = await res.json();
  assert.deepEqual(data, { status: "cleared", count: 0 });
});

test("createInterceptedFetch routes POST /api/library/add to addToLibrary", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/library/add", { method: "POST", body: JSON.stringify({ video_id: "v1", title: "T", artist: "", category: "Outros" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.video_id, "v1");
});

test("createInterceptedFetch routes POST /api/library/remove to removeFromLibrary", async () => {
  const storage = fakeStorage();
  const libraryData = {};
  addToLibrary(storage, libraryData, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => libraryData, searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/library/remove", { method: "POST", body: JSON.stringify({ video_id: "v1" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.removed_count, 1);
});

test("createInterceptedFetch routes POST /api/library/move to moveInLibrary", async () => {
  const storage = fakeStorage();
  const libraryData = {};
  addToLibrary(storage, libraryData, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => libraryData, searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/library/move", { method: "POST", body: JSON.stringify({ video_id: "v1", new_category: "Samba & Pagode", old_category: "Outros" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.new_category, "Samba & Pagode");
});

test("createInterceptedFetch routes POST /api/suggestions/discover to discoverTracks", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({
    originalFetch: async () => { throw new Error("no network"); }, storage,
    getLibraryData: () => ({}),
    searchFnForYoutube: async () => ({ tracks: [{ video_id: "v1", title: "T", artist: "" }] }),
  });
  const res = await fetchFn("/api/suggestions/discover", { method: "POST", body: JSON.stringify({ category: "Samba & Pagode" }) });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.category, "Samba & Pagode");
  assert.equal(data.tracks.length, 1);
});

test("createInterceptedFetch routes GET /api/suggestions/related to discoverRelatedTracks", async () => {
  const storage = fakeStorage();
  const fetchFn = createInterceptedFetch({
    originalFetch: async () => { throw new Error("no network"); }, storage,
    getLibraryData: () => ({}),
    searchFnForYoutube: async () => ({ tracks: [] }),
  });
  const res = await fetchFn("/api/suggestions/related?title=Some+Song&artist=Some+Artist&category=Outros&video_id=cur1");
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.title, "Some Song");
});

test("createInterceptedFetch routes POST /api/suggestions/reset-seen to clear the seen-ids key", async () => {
  const storage = fakeStorage();
  storage.setItem("seen_suggested_ids", JSON.stringify(["a", "b"]));
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/suggestions/reset-seen", { method: "POST" });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(storage.getItem("seen_suggested_ids"), null);
});

test("createInterceptedFetch routes POST /api/sync-youtube to a watch_videos URL built from the local queue", async () => {
  const storage = fakeStorage();
  addToQueue(storage, { video_id: "v1", title: "T", artist: "", category: "Outros" });
  const fetchFn = createInterceptedFetch({ originalFetch: async () => { throw new Error("no network"); }, storage, getLibraryData: () => ({}), searchFnForYoutube: async () => ({ tracks: [] }) });
  const res = await fetchFn("/api/sync-youtube", { method: "POST" });
  const data = await res.json();
  assert.equal(data.success, true);
  assert.equal(data.playlist_url, "https://www.youtube.com/watch_videos?video_ids=v1");
});

// --- Quota degradation ---

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

// --- Storage unavailable (private mode) ---

test("getQueue falls back to an empty list when storage.getItem throws", () => {
  const storage = { getItem: () => { throw new Error("blocked"); }, setItem: () => { throw new Error("blocked"); } };
  assert.deepEqual(getQueue(storage), []);
});
