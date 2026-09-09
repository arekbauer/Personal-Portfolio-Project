# Managing website content

The website content is stored as JSON in `src/content`, and local images are
stored in `public/media`. You no longer need Django Admin or `db.sqlite3` for
normal content updates.

Node.js 24 is recommended. Before making an update, create a branch from the
latest version of `main`:

```powershell
git switch main
git pull
git switch -c content/short-description
```

Run the local development server while editing:

```powershell
npm ci
npm run dev
```

The site will normally be available at <http://localhost:4321> and will refresh
as files change.

## Adding a recipe

Generate a starter recipe file:

```powershell
npm run new:recipe -- "Chicken Tikka Masala"
```

This creates `src/content/recipes/chicken-tikka-masala.json`. Edit the generated
file to provide the real recipe information:

```json
{
  "title": "Chicken Tikka Masala",
  "slug": "chicken-tikka-masala",
  "image": "recipes/images/chicken-tikka-masala.webp",
  "baseServings": 4,
  "imageCredit": "",
  "imageCreditUrl": "",
  "sourceName": "",
  "sourceUrl": "",
  "categories": ["Dinner", "Curry"],
  "ingredients": [
    {
      "amount": 500,
      "unit": "g",
      "name": "chicken breast",
      "note": "diced",
      "section": "Chicken"
    }
  ],
  "steps": [
    "Describe the first step.",
    "Describe the second step."
  ]
}
```

Important fields:

- `slug` becomes the URL and must contain lowercase letters, numbers and
  hyphens only.
- `baseServings` controls the initial serving count and ingredient calculator.
- `amount` must be a positive number or `null` for ingredients without a
  measurable amount.
- Consecutive ingredients with the same `section` are displayed together.
- `imageCreditUrl` and `sourceUrl` must either be empty strings or complete
  URLs.
- Every recipe needs at least one category, ingredient and method step.

Add the image at:

```text
public/media/recipes/images/chicken-tikka-masala.webp
```

The image path in JSON is relative to `public/media`, so it does not include
`public/media` at the beginning. Recipes are displayed alphabetically by title.

To remove a recipe, delete its JSON file and remove its image if nothing else
uses it.

## Changing the intro

Edit `src/content/site.json`:

```json
{
  "intros": [
    {
      "description": "Your updated introduction...",
      "image": "portfolio/images/profile_picture.jpg",
      "image_small": "portfolio/images/profile_picture-square.jpg"
    }
  ]
}
```

The description supports the HTML formatting already used by the website. For
example:

```json
"description": "I build <span>Android applications</span>.<br><br>Outside of work, I enjoy cooking."
```

Keep the file valid JSON. Double quotes written inside the description must be
escaped as `\"`.

To replace the profile images, put the new files under
`public/media/portfolio/images` and either keep the existing filenames or
update `image` and `image_small` to match the new filenames.

## Adding a project

Generate a starter project file:

```powershell
npm run new:project -- "My New App"
```

This creates `src/content/projects/my-new-app.json`. Edit it with the project's
real details:

```json
{
  "order": 100,
  "title": "My New App",
  "description": "A short explanation of the project.",
  "image": "portfolio/images/my-new-app.webp",
  "url": "https://example.com",
  "skills": ["Kotlin", "Jetpack Compose"]
}
```

Important fields:

- `order` controls placement. Projects with higher numbers appear first.
- `url` must be a complete URL.
- `skills` can contain up to four entries.
- `description` supports the existing HTML formatting when needed.

Add the project image at:

```text
public/media/portfolio/images/my-new-app.webp
```

To remove a project, delete its JSON file and remove its image if nothing else
uses it.

## Managing albums

Albums are stored together in `src/content/albums.json`. Add another object to
the JSON array:

```json
{
  "title": "Album title",
  "artist": "Artist name",
  "featured": true,
  "spotifyAlbumId": "spotify-album-id",
  "coverImageUrl": "https://example.com/album-cover.jpg",
  "spotifyUrl": "https://open.spotify.com/album/spotify-album-id",
  "releaseDate": "2026-01-31",
  "displayOrder": 0
}
```

- Only albums with `featured` set to `true` are displayed.
- Albums are automatically ordered by `releaseDate`, newest first.
- Use the `YYYY-MM-DD` format for release dates.
- Album covers currently use remote image URLs, so no local image is required.

Remove an album by deleting its complete object from the array. Take care with
the comma between neighbouring objects so the file remains valid JSON.

## Managing slabs

Slabs are stored together in `src/content/slabs.json`. Add another object to the
JSON array:

```json
{
  "cardId": "set-number",
  "name": "Card name",
  "setName": "Set name",
  "number": "123",
  "rarity": "Illustration Rare",
  "grader": "PSA",
  "grade": "10",
  "certificationNumber": "",
  "image": "https://example.com/card-image.png",
  "featured": true,
  "displayOrder": 1
}
```

- Only slabs with `featured` set to `true` are displayed.
- Lower `displayOrder` numbers appear first.
- `certificationNumber` may be an empty string.
- `image` may be a complete remote URL or a path relative to `public/media`.

For a local image, use a value such as:

```json
"image": "portfolio/images/slabs/my-card.webp"
```

and save the file as:

```text
public/media/portfolio/images/slabs/my-card.webp
```

## Validate and publish an update

Before committing any content change, run:

```powershell
npm test
npm run build
```

Both commands should finish successfully. Then commit and push the branch:

```powershell
git add src/content public/media
git commit -m "Describe the content update"
git push -u origin content/short-description
```

Open a pull request into `main`. Review the Cloudflare preview and merge the pull
request when it looks correct. Once merged, Cloudflare automatically deploys
the updated `main` branch to the production website.

