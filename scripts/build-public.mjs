import { cp, mkdir, rm } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

// What the hosted page actually fetches (checked against player.html's own
// <link>/<script> tags) — not the rest of the repo (Python scripts, docs,
// the planning ledger, personal JSON files), which `publish = "."` would
// otherwise serve at public URLs on Netlify.
export const PUBLIC_ENTRIES = ["player.html", "assets"];

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const PUBLIC_DIR = path.join(ROOT, "public");

export async function buildPublic() {
  await rm(PUBLIC_DIR, { recursive: true, force: true });
  await mkdir(PUBLIC_DIR, { recursive: true });
  for (const entry of PUBLIC_ENTRIES) {
    await cp(path.join(ROOT, entry), path.join(PUBLIC_DIR, entry), { recursive: true });
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await buildPublic();
  console.log(`Built ${PUBLIC_DIR} from: ${PUBLIC_ENTRIES.join(", ")}`);
}
