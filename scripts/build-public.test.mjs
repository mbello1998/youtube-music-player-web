import { test } from "node:test";
import assert from "node:assert/strict";
import { PUBLIC_ENTRIES, shouldExcludeFromPublic } from "./build-public.mjs";

test("PUBLIC_ENTRIES lists only what the hosted page actually serves — not the whole repo", () => {
  assert.deepEqual(PUBLIC_ENTRIES, ["player.html", "assets"]);
});

test("shouldExcludeFromPublic excludes test files from the published assets/ copy", () => {
  assert.equal(shouldExcludeFromPublic("C:\\project\\assets\\js\\discovery.test.mjs"), true);
  assert.equal(shouldExcludeFromPublic("C:\\project\\assets\\js\\local-state-api.test.mjs"), true);
  assert.equal(shouldExcludeFromPublic("C:\\project\\assets\\js\\discovery.js"), false);
  assert.equal(shouldExcludeFromPublic("C:\\project\\assets\\css\\player.css"), false);
});
