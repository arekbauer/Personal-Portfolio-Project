import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { test } from "node:test";

const recipesDirectory = new URL("../src/content/recipes/", import.meta.url);

test("recipe slugs, filenames, and required content are valid", async () => {
  const files = (await readdir(recipesDirectory)).filter((file) => file.endsWith(".json"));
  assert.ok(files.length > 0, "expected at least one recipe");
  for (const file of files) {
    const recipe = JSON.parse(await readFile(new URL(file, recipesDirectory), "utf8"));
    assert.equal(file, `${recipe.slug}.json`);
    assert.ok(recipe.title);
    assert.ok(recipe.ingredients.length > 0);
    assert.ok(recipe.steps.length > 0);
    assert.ok(recipe.image, `missing image path for ${recipe.title}`);
  }
});
