import { z } from "zod";
import albumsSource from "../content/albums.json";
import siteSource from "../content/site.json";
import slabsSource from "../content/slabs.json";

const optionalText = z.string().default("");

const projectSchema = z.object({
  order: z.number().int(),
  title: z.string().min(1),
  description: z.string().min(1),
  image: z.string().min(1),
  url: z.string().url(),
  skills: z.array(z.string()).max(4),
});

const ingredientSchema = z.object({
  amount: z.number().positive().nullable(),
  unit: optionalText,
  name: z.string().min(1),
  note: optionalText,
  section: optionalText,
});

const recipeSchema = z.object({
  title: z.string().min(1),
  slug: z.string().regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  image: z.string().min(1),
  baseServings: z.number().int().positive(),
  imageCredit: optionalText,
  imageCreditUrl: z.union([z.literal(""), z.string().url()]),
  sourceName: optionalText,
  sourceUrl: z.union([z.literal(""), z.string().url()]),
  categories: z.array(z.string().min(1)).min(1),
  ingredients: z.array(ingredientSchema).min(1),
  steps: z.array(z.string().min(1)).min(1),
});

const albumSchema = z.object({
  spotifyAlbumId: z.string().min(1),
  title: z.string().min(1),
  artist: z.string().min(1),
  coverImageUrl: z.string().url(),
  spotifyUrl: z.string().url(),
  releaseDate: z.string().nullable(),
  featured: z.boolean(),
  displayOrder: z.number().int(),
});

const slabSchema = z.object({
  cardId: z.string().min(1),
  name: z.string().min(1),
  setName: optionalText,
  number: optionalText,
  rarity: optionalText,
  grader: z.string().min(1),
  grade: z.string().min(1),
  certificationNumber: optionalText,
  image: z.string().min(1),
  featured: z.boolean(),
  displayOrder: z.number().int(),
});

const siteSchema = z.object({
  intros: z.array(
    z.object({
      description: z.string().min(1),
      image: z.string().min(1),
      image_small: z.string().min(1),
    }),
  ).min(1),
});

const projectFiles = import.meta.glob("../content/projects/*.json", {
  eager: true,
  import: "default",
});
const recipeFiles = import.meta.glob("../content/recipes/*.json", {
  eager: true,
  import: "default",
});

export type Project = z.infer<typeof projectSchema>;
export type Recipe = z.infer<typeof recipeSchema>;
export type Ingredient = z.infer<typeof ingredientSchema>;

export const site = siteSchema.parse(siteSource);
export const projects = Object.values(projectFiles)
  .map((project) => projectSchema.parse(project))
  .sort((a, b) => b.order - a.order);
export const recipes = Object.values(recipeFiles)
  .map((recipe) => recipeSchema.parse(recipe))
  .sort((a, b) => a.title.localeCompare(b.title));
export const albums = z.array(albumSchema).parse(albumsSource)
  .filter((album) => album.featured)
  .sort((a, b) => (b.releaseDate ?? "").localeCompare(a.releaseDate ?? ""));
export const slabs = z.array(slabSchema).parse(slabsSource)
  .filter((slab) => slab.featured)
  .sort((a, b) => a.displayOrder - b.displayOrder);

export function mediaUrl(path: string): string {
  return path.startsWith("http") ? path : `/media/${path}`;
}

export function groupIngredients(ingredients: Ingredient[]) {
  const sections: Array<{ name: string; items: Ingredient[] }> = [];
  for (const ingredient of ingredients) {
    const previous = sections.at(-1);
    if (!previous || previous.name !== ingredient.section) {
      sections.push({ name: ingredient.section, items: [ingredient] });
    } else {
      previous.items.push(ingredient);
    }
  }
  return sections;
}
