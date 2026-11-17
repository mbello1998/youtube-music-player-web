import { test } from "node:test";
import assert from "node:assert/strict";
import {
  detectOrEstimateBpm,
  resolveOfficialCategory,
  GENRE_SEARCH_QUERIES,
  getNextQuery,
  collectExcludedIds,
  discoverTracks,
  discoverRelatedTracks,
} from "./discovery.js";

function fakeStorage() {
  const map = new Map();
  return {
    getItem: (key) => (map.has(key) ? map.get(key) : null),
    setItem: (key, value) => {
      map.set(key, value);
    },
  };
}

test("detectOrEstimateBpm reads an explicit BPM from the title", () => {
  assert.equal(detectOrEstimateBpm("Ritmada Pesada 135 BPM", "Outros"), 135);
});

test("detectOrEstimateBpm falls back to a deterministic in-range estimate", () => {
  const first = detectOrEstimateBpm("Some Track Title", "Sertanejo Antigo & Modão");
  const second = detectOrEstimateBpm("Some Track Title", "Sertanejo Antigo & Modão");
  assert.equal(first, second); // deterministic
  assert.ok(first >= 80 && first <= 110); // within that category's range
});

test("resolveOfficialCategory matches funk keywords", () => {
  assert.equal(resolveOfficialCategory("MC Fulano - Montagem Pesada", ""), "Funk Paulista, BH & Mandelão");
});

test("resolveOfficialCategory falls back to Outros", () => {
  assert.equal(resolveOfficialCategory("Completely Unrelated Title", "Unknown Artist"), "Outros");
});

test("getNextQuery rotates through the category's query list and persists the index", () => {
  const storage = fakeStorage();
  const queries = GENRE_SEARCH_QUERIES["Samba & Pagode"];
  assert.equal(getNextQuery("Samba & Pagode", storage), queries[0]);
  assert.equal(getNextQuery("Samba & Pagode", storage), queries[1]);
});

test("collectExcludedIds unions library, queue and seen ids", () => {
  const ids = collectExcludedIds({
    libraryData: { Outros: [{ video_id: "lib1" }] },
    queue: [{ video_id: "q1" }],
    seenIds: ["seen1"],
  });
  assert.deepEqual([...ids].sort(), ["lib1", "q1", "seen1"]);
});

test("discoverTracks excludes known ids and sorts by closeness to the seed BPM", async () => {
  const storage = fakeStorage();
  const searchFn = async () => ({
    tracks: [
      { video_id: "known", title: "Already have 130 BPM", artist: "" },
      { video_id: "far", title: "Far Track 90 BPM", artist: "" },
      { video_id: "close", title: "Close Track 128 BPM", artist: "" },
    ],
  });
  const results = await discoverTracks({
    category: "Mega Funk & Ritmadas",
    seedBpm: 130,
    limit: 10,
    storage,
    libraryData: { Outros: [{ video_id: "known" }] },
    queue: [],
    searchFn,
  });
  assert.deepEqual(results.map((t) => t.video_id), ["close", "far"]); // "known" excluded, closest first
});

test("discoverRelatedTracks issues at most 2 searches", async () => {
  const storage = fakeStorage();
  let callCount = 0;
  const searchFn = async () => {
    callCount++;
    return { tracks: [] };
  };
  await discoverRelatedTracks({
    title: "Some Song",
    artist: "Some Artist",
    category: "Mega Funk & Ritmadas",
    currentVideoId: "cur1",
    targetBpm: 130,
    limit: 10,
    storage,
    libraryData: {},
    queue: [],
    searchFn,
  });
  assert.ok(callCount <= 2);
});
