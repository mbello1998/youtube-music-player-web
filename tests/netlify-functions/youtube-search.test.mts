import { test } from "node:test";
import assert from "node:assert/strict";
import { searchYouTube } from "../../netlify/functions/youtube-search.mts";

// Mirrors the real @netlify/blobs store: get() returns the raw string by
// default and only returns the parsed value when { type: "json" } is passed
// (node_modules/@netlify/blobs/dist/main.d.ts:131-145). setJSON stores the
// JSON-encoded string, same as the real store does on disk.
function realisticBlobStore() {
  const store = new Map<string, string>();
  return {
    get: async (k: string, opts?: { type?: "json" }) => {
      const raw = store.get(k);
      if (raw === undefined) return null;
      return opts?.type === "json" ? JSON.parse(raw) : raw;
    },
    setJSON: async (k: string, v: unknown) => {
      store.set(k, JSON.stringify(v));
    },
  };
}

function okResponse(videoId: string, title: string, channelTitle: string) {
  return new Response(
    JSON.stringify({
      items: [{ id: { videoId }, snippet: { title, channelTitle } }],
    }),
    { status: 200 },
  );
}

test("searchYouTube calls the YouTube API and caches the result", async () => {
  const fetchCalls: string[] = [];
  const fetchImpl = async (url: string) => {
    fetchCalls.push(url);
    return okResponse("abc123", "Song Title", "Some Channel");
  };
  const blobStore = realisticBlobStore();

  const result = await searchYouTube({
    query: "mega funk 2024",
    limit: 10,
    apiKey: "FAKE_KEY",
    fetchImpl,
    blobStore,
  });

  assert.equal(fetchCalls.length, 1);
  assert.ok(fetchCalls[0].includes("key=FAKE_KEY"));
  assert.deepEqual(result.tracks, [
    { video_id: "abc123", title: "Song Title", artist: "Some Channel" },
  ]);
});

test("searchYouTube returns the cached result on a repeat query without calling fetch again", async () => {
  let fetchCallCount = 0;
  const fetchImpl = async () => {
    fetchCallCount++;
    return okResponse("abc123", "Song Title", "Some Channel");
  };
  const blobStore = realisticBlobStore();

  await searchYouTube({ query: "Mega Funk 2024", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });
  const second = await searchYouTube({ query: "mega funk 2024  ", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.equal(fetchCallCount, 1);
  assert.equal(second.tracks[0].video_id, "abc123");
  assert.equal(Array.isArray(second.tracks), true);
});

test("searchYouTube returns quotaExceeded (not a throw) when the network call itself fails", async () => {
  const fetchImpl = async () => {
    throw new Error("network down");
  };
  const blobStore = realisticBlobStore();

  const result = await searchYouTube({ query: "funk", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.deepEqual(result, { tracks: [], quotaExceeded: true });
});

test("searchYouTube returns quotaExceeded when the response body isn't valid JSON", async () => {
  const fetchImpl = async () => new Response("<html>not json</html>", { status: 200 });
  const blobStore = realisticBlobStore();

  const result = await searchYouTube({ query: "funk", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.deepEqual(result, { tracks: [], quotaExceeded: true });
});

test("searchYouTube returns quotaExceeded on a non-2xx response", async () => {
  const fetchImpl = async () => new Response("{}", { status: 403 });
  const blobStore = realisticBlobStore();

  const result = await searchYouTube({ query: "funk", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.deepEqual(result, { tracks: [], quotaExceeded: true });
});
