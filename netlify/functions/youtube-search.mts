import { getStore } from "@netlify/blobs";

export type Track = {
  video_id: string;
  title: string;
  artist: string;
};

export type SearchResult = {
  tracks: Track[];
  quotaExceeded?: boolean;
};

export type BlobStore = {
  get: (key: string) => Promise<unknown>;
  setJSON: (key: string, value: unknown) => Promise<void>;
};

export type SearchYouTubeArgs = {
  query: string;
  limit: number;
  apiKey: string;
  fetchImpl: (url: string) => Promise<Response>;
  blobStore: BlobStore;
};

function cacheKey(query: string, limit: number): string {
  return `${query.trim().toLowerCase()}::${limit}`;
}

export async function searchYouTube({
  query,
  limit,
  apiKey,
  fetchImpl,
  blobStore,
}: SearchYouTubeArgs): Promise<SearchResult> {
  const key = cacheKey(query, limit);
  const cached = await blobStore.get(key);
  if (cached) {
    return cached as SearchResult;
  }

  const url = `https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=${limit}&q=${encodeURIComponent(query)}&key=${apiKey}`;
  const response = await fetchImpl(url);

  if (!response.ok) {
    return { tracks: [], quotaExceeded: true };
  }

  const data = (await response.json()) as {
    items?: Array<{ id?: { videoId?: string }; snippet?: { title?: string; channelTitle?: string } }>;
  };

  const tracks: Track[] = (data.items || [])
    .filter((item) => item.id?.videoId && item.snippet?.title)
    .map((item) => ({
      video_id: item.id!.videoId as string,
      title: item.snippet!.title as string,
      artist: item.snippet?.channelTitle || "",
    }));

  const result: SearchResult = { tracks };
  await blobStore.setJSON(key, result);
  return result;
}

export default async (req: Request) => {
  const url = new URL(req.url);
  const query = url.searchParams.get("q") || "";
  const limit = Number(url.searchParams.get("limit")) || 15;
  const result = await searchYouTube({
    query,
    limit,
    apiKey: Netlify.env.get("YOUTUBE_API_KEY") || "",
    fetchImpl: fetch,
    blobStore: getStore("youtube-search-cache"),
  });
  return Response.json(result);
};

export const config = { path: "/api/youtube-search" };
