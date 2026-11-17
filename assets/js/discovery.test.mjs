import { test } from "node:test";
import assert from "node:assert/strict";
import { detectOrEstimateBpm, resolveOfficialCategory } from "./discovery.js";

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
