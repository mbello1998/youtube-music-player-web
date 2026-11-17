import { test } from "node:test";
import assert from "node:assert/strict";
import { searchYouTube } from "../../netlify/functions/youtube-search.mts";

test("searchYouTube calls the YouTube API and caches the result", async () => {
  const fetchCalls: string[] = [];
  const fetchImpl = async (url: string) => {
    fetchCalls.push(url);
    return new Response(
      JSON.stringify({
        items: [
          {
            id: { videoId: "abc123" },
            snippet: { title: "Song Title", channelTitle: "Some Channel" },
          },
        ],
      }),
      { status: 200 },
    );
  };
  const store = new Map<string, unknown>();
  const blobStore = {
    get: async (k: string) => store.get(k) ?? null,
    setJSON: async (k: string, v: unknown) => {
      store.set(k, v);
    },
  };

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
    return new Response(
      JSON.stringify({
        items: [
          {
            id: { videoId: "abc123" },
            snippet: { title: "Song Title", channelTitle: "Some Channel" },
          },
        ],
      }),
      { status: 200 },
    );
  };
  const store = new Map<string, unknown>();
  const blobStore = {
    get: async (k: string) => store.get(k) ?? null,
    setJSON: async (k: string, v: unknown) => {
      store.set(k, v);
    },
  };

  await searchYouTube({ query: "Mega Funk 2024", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });
  const second = await searchYouTube({ query: "mega funk 2024  ", limit: 10, apiKey: "FAKE_KEY", fetchImpl, blobStore });

  assert.equal(fetchCallCount, 1);
  assert.equal(second.tracks[0].video_id, "abc123");
});
