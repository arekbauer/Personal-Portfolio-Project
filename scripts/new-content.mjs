import { mkdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const [kind, ...titleParts] = process.argv.slice(2);
const title = titleParts.join(" ").trim();

if (!['recipe', 'project'].includes(kind) || !title) {
  console.error('Usage: npm run new:recipe -- "Recipe title" or npm run new:project -- "Project title"');
  process.exit(1);
}

const slug = title.toLowerCase().normalize("NFKD").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
const directory = resolve(`src/content/${kind}s`);
const path = resolve(directory, `${slug}.json`);
if (existsSync(path)) {
  console.error(`Content already exists: ${path}`);
  process.exit(1);
}

const value = kind === "recipe"
  ? {
      title, slug, image: `recipes/images/${slug}.webp`, baseServings: 4,
      imageCredit: "", imageCreditUrl: "", sourceName: "", sourceUrl: "",
      categories: ["Dinner"],
      ingredients: [{ amount: 1, unit: "", name: "Ingredient", note: "", section: "Ingredients" }],
      steps: ["Describe the first step."],
    }
  : {
      order: Date.now(), title, description: "Describe the project.",
      image: `portfolio/images/${slug}.webp`, url: "https://example.com", skills: [],
    };

await mkdir(directory, { recursive: true });
await writeFile(path, `${JSON.stringify(value, null, 2)}\n`, "utf8");
console.log(`Created ${path}`);
console.log(`Add its image under public/media/${value.image}, then run npm run dev.`);
