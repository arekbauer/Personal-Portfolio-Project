# arekbauer.com

Arek Bauer's portfolio, recipes, album picks, and Pokémon slab collection. The
new site is statically generated with Astro and deployed through Cloudflare
Pages. Cloudflare Pages Functions provide the Spotify and TRMNL API routes.

The legacy Django application remains in this branch temporarily as a migration
reference. Cloudflare builds only the Astro application.

## Local development

Node.js 24 is recommended (22.12 or newer is required).

```sh
npm install
npm run dev
```

`npm run dev` serves the static site. To exercise Cloudflare Functions locally,
create an untracked `.env` with the keys from `.env.example`, then run:

```sh
npm run build
npm run preview
```

## Add content

Create a starter recipe or project:

```sh
npm run new:recipe -- "Recipe name"
npm run new:project -- "Project name"
```

Edit the generated JSON under `src/content`, add its image under `public/media`,
then use `npm run dev` to preview it. `npm run build` validates every content
record before producing the site.

Album picks and slabs live in `src/content/albums.json` and
`src/content/slabs.json` respectively.

## Deployment

See [docs/cloudflare-setup.md](docs/cloudflare-setup.md) for the one-time account,
Git integration, secrets, preview, domain, and cutover steps.
