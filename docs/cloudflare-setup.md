# Cloudflare setup and cutover

The repository is ready for Cloudflare Pages, but the following account-level
steps must be completed by the owner of `arekbauer.com`.

## 1. Push and review the migration branch

Push `codex/cloudflare-migration` to GitHub and open a pull request into `main`.
Do not merge it or cancel PythonAnywhere yet. Confirm that the `Validate website`
GitHub check passes.

## 2. Create the Cloudflare Pages project

In **Cloudflare Dashboard → Workers & Pages → Create → Pages → Connect to Git**:

- Select the `arekbauer/arekbauer.com` repository.
- Production branch: `main`.
- Framework preset: `Astro` (or `None` with the values below).
- Build command: `npm run build`.
- Build output directory: `dist`.
- Root directory: leave blank.
- Set `NODE_VERSION` to `24` if the build environment does not already use it.

Enable preview deployments for non-production branches. Cloudflare will create a
temporary `*.pages.dev` URL for the migration branch and for its pull request.

## 3. Add Function secrets

Under the Pages project's **Settings → Variables and Secrets**, add these as
encrypted secrets for both Preview and Production:

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `SPOTIFY_REFRESH_TOKEN`
- `POKEMON_TCG_API_KEY` (optional, but recommended)

Copy the values from the existing PythonAnywhere configuration. Never paste them
into a committed file or a pull request.

## 4. Final content and media sync

The branch was seeded from the local ignored `db.sqlite3` and local `media`
directory. Before cutover, download fresh copies from PythonAnywhere and run:

```sh
python scripts/export_cloudflare_content.py path/to/production/db.sqlite3
```

Copy the production `media/portfolio` and `media/recipes` directories into
`public/media`, then rebuild. In particular, the local checkout is missing
`recipes/images/creamy-pasta.webp`, referenced by Tomato Beef Pasta.

## 5. Verify the preview

Check these routes on the Cloudflare preview URL:

- `/`
- `/recipes/` and every recipe detail page
- `/albums/`
- `/slabs/`
- `/api/now-playing/`
- `/api/trmnl/vct-ticker/`
- `/api/trmnl/pokemon-card-of-the-day/`

Also confirm the light/dark theme, mobile navigation, recipe filtering, serving
adjustments, external links, images, and TRMNL device rendering.

## 6. Merge and connect the domain

After preview approval, merge into `main`. Wait for the production Pages build
to succeed, then add `www.arekbauer.com` under **Custom domains**. Follow the DNS
record Cloudflare provides. Keep the existing apex-domain redirect to `www`, or
attach the apex domain and redirect it at Cloudflare.

DNS changes can take time to propagate. Keep PythonAnywhere active until the
custom domain, APIs, and TRMNL device have worked through at least one normal day.

## 7. Retire PythonAnywhere

Take one final backup of the SQLite database and media files. Only then cancel
the PythonAnywhere subscription. The legacy Django source can be removed from a
later cleanup branch after the Cloudflare deployment has proven stable.
