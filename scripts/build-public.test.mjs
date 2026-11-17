import { test } from "node:test";
import assert from "node:assert/strict";
import { PUBLIC_ENTRIES } from "./build-public.mjs";

test("PUBLIC_ENTRIES lists only what the hosted page actually serves — not the whole repo", () => {
  assert.deepEqual(PUBLIC_ENTRIES, ["player.html", "assets"]);
});
