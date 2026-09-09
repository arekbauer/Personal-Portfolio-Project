# Cloudflare setup and cutover

This is the complete first-time setup for moving `www.arekbauer.com` from
PythonAnywhere to Cloudflare Pages.

The intended arrangement is:

- Porkbun remains the domain registrar. The domain does not need to be
  transferred.
- Cloudflare Free becomes the DNS provider and hosts the website.
- GitHub remains the source of truth.
- A push to a branch creates a preview deployment.
- A push to `main` updates the live website after the migration is complete.
- Secret API credentials live in Cloudflare, not in GitHub.

No paid Cloudflare plan, database product, storage product, or payment card is
required for this website. Do not cancel PythonAnywhere until the final checks
in this document have passed.

## Before starting

Do not push the migration branch until the public-repository review items have
been resolved:

1. Strip metadata from the public portrait and Booklio images.
2. Confirm that every recipe image can legally be republished, replacing any
   image whose licence or ownership is uncertain.
3. Change the password represented by the old Django password hash if that
   password was used anywhere else.

Also have access to all of the following:

- The email account that will own the Cloudflare account.
- The GitHub account that owns or can administer the repository.
- The Porkbun account that manages `arekbauer.com`.
- The existing Spotify credentials, ideally from the local ignored `.env`
  file or the PythonAnywhere configuration.
- A password manager in which to save recovery codes.

## Phase 1: Create and secure the Cloudflare account

1. Open <https://dash.cloudflare.com/sign-up>.
2. Enter the email address that should permanently own the website and a new,
   unique password.
3. Select **Create account**.
4. Open the verification message sent by Cloudflare and verify the email
   address.
5. Return to the Cloudflare dashboard.
6. Open the profile menu in the top-right corner, then select
   **My Profile → Authentication**.
7. Add at least one strong two-factor authentication method. Windows Hello or
   a security key is preferable; an authenticator app is also suitable.
8. Save the Cloudflare backup codes in the password manager. Do not store them
   in this repository.

If Cloudflare immediately offers to add a domain, it is safe to skip that step
for now. The website will be deployed and tested before DNS is moved.

If a plan picker appears at any point, select **Free**. Do not select Workers
Paid, Pro, Business, R2, D1, or any other paid product for this migration.

## Phase 2: Push the reviewed migration branch

After the repository review blockers have been fixed and the branch has been
reviewed again:

```powershell
git status
git push -u origin codex/cloudflare-migration
```

On GitHub:

1. Open the repository.
2. Create a pull request from `codex/cloudflare-migration` into `main`.
3. Wait for the **Validate website** GitHub Actions check to pass.
4. Leave the pull request open. Do not merge it yet.

The branch has to exist on GitHub before Cloudflare can select it.

## Phase 3: Create the Cloudflare Pages project

1. Open <https://dash.cloudflare.com/> and select the Cloudflare account.
2. In the sidebar, open **Workers & Pages**.
3. Select **Create application**.
4. Select the **Pages** tab.
5. Select **Import an existing Git repository** or **Connect to Git**. The
   precise button text may differ slightly as Cloudflare updates the dashboard.
6. Select **GitHub**.
7. GitHub will ask permission to install or authorize Cloudflare Pages. Choose
   **Only select repositories**, then select this portfolio repository. Avoid
   granting access to every repository unless that is genuinely desired.
8. Return to Cloudflare and select the portfolio repository.
9. Select **Begin setup**.

Before continuing, confirm that this is the **Pages** setup form. The correct
form asks for a production branch, framework preset, build command, build
output directory, and root directory. It does not ask for a deploy command or
a version/non-production deploy command.

If the form contains either of these defaults, go back because Cloudflare has
opened the **Workers Builds** wizard instead:

```text
Deploy command: npx wrangler deploy
Version or non-production command: npx wrangler versions upload
```

Those commands deploy a Worker script and are not valid for this Pages
project. Return to **Workers & Pages → Create application**, explicitly select
the **Pages** tab, and choose the Pages Git integration. Do not work around the
wrong wizard by changing the deploy command to `wrangler pages deploy`; that
would create a different Direct Upload workflow instead of the intended native
Pages Git integration.

Use these exact project values:

| Cloudflare option | Value |
| --- | --- |
| Project name | `arekbauer-com` |
| Production branch, initially | `codex/cloudflare-migration` |
| Framework preset | `Astro` |
| Build command | `npm run build` |
| Build output directory | `dist` |
| Root directory | Leave blank |

The migration branch is deliberately used as the initial production branch.
At this stage, “production” only means the main `pages.dev` address; the real
domain still points to PythonAnywhere. This allows the complete migrated site,
including Pages Functions, to be tested before merging.

Under environment variables or advanced build settings, add this plain-text
build variable:

| Name | Value | Type |
| --- | --- | --- |
| `NODE_VERSION` | `24` | Plain text |

Add it to **Production** and **Preview** if Cloudflare asks which environment it
belongs to. Node 24 matches local development and GitHub Actions. It is not a
secret.

Select **Save and Deploy**. Cloudflare will install dependencies, run the
build, and publish the result. The first build should end with a success state
and provide an address similar to:

```text
https://arekbauer-com.pages.dev
```

If the requested project name is unavailable, use a close alternative and use
the actual `pages.dev` address Cloudflare assigns in all later steps.

## Phase 4: Add the runtime secrets

The static pages build without API credentials, but the Spotify and optional
Pokémon endpoints need runtime secrets.

In Cloudflare:

1. Open **Workers & Pages**.
2. Select the `arekbauer-com` Pages project.
3. Open **Settings → Variables and Secrets**.
4. Select **Add**.
5. Add each variable below.
6. For each credential, select **Encrypt** before saving it.

| Name | Required? | Type |
| --- | --- | --- |
| `SPOTIFY_CLIENT_ID` | Yes, for the Spotify widget | Secret/encrypted |
| `SPOTIFY_CLIENT_SECRET` | Yes, for the Spotify widget | Secret/encrypted |
| `SPOTIFY_REFRESH_TOKEN` | Yes, for the Spotify widget | Secret/encrypted |
| `POKEMON_TCG_API_KEY` | Optional but recommended | Secret/encrypted |

Add the same names and values to both environments:

- **Production** is currently the migration branch and later becomes `main`.
- **Preview** is used for pull requests and other branches.

Never paste the values into `.env.example`, `wrangler.jsonc`, GitHub, a pull
request, an issue, or this document. Cloudflare will not display an encrypted
secret again after it is saved; that is expected.

After saving the secrets, make a new deployment so the Functions receive them:

1. Open the project’s **Deployments** page.
2. Open the most recent deployment.
3. Select **Retry deployment**, or push another harmless commit to the branch.
4. Wait for the new deployment to succeed.

## Phase 5: Configure automatic deployments

Open the project and go to
**Settings → Builds & deployments → Branch control**.

For the initial test period, use:

| Option | Setting |
| --- | --- |
| Production branch | `codex/cloudflare-migration` |
| Automatic production deployments | Enabled |
| Preview deployments | All non-production branches |

This gives every future pull request a separate preview address. Preview
deployments are separate from the live custom domain and Cloudflare adds a
`noindex` response header to them by default.

After the migration is merged, the production branch will be changed to
`main`. Do not change it yet.

## Phase 6: Test the `pages.dev` deployment

Do this before adding the domain or changing nameservers.

Open each page:

- `/`
- `/recipes/`
- Every individual recipe
- `/albums/`
- `/slabs/`

Check the following on both desktop and a phone-sized browser window:

- Header height and navigation.
- Light and dark themes.
- Social icons and links.
- Intro positioning.
- Three-column project layout on desktop.
- Recipe filtering and serving-size controls.
- Every local image.
- Every external link.

Open these API addresses directly and confirm that each returns JSON rather
than an HTML error page:

- `/api/now-playing/`
- `/api/trmnl/vct-ticker/`
- `/api/trmnl/pokemon-card-of-the-day/`

The Spotify response should report either a playing/recent track or a normal
“nothing playing” state. A message about missing configuration means the
Spotify secrets were not added to the environment used by that deployment.

Also confirm the TRMNL integrations against the `pages.dev` API addresses if a
TRMNL device or recipe configuration is available.

Do not continue until all of these checks pass.

## Phase 7: Merge and make `main` the production branch

Once the preview is approved:

1. Merge the pull request into `main` on GitHub.
2. In Cloudflare, open
   **Settings → Builds & deployments → Branch control**.
3. Change **Production branch** from `codex/cloudflare-migration` to `main`.
4. Keep automatic production deployments enabled.
5. Trigger a deployment of `main` if Cloudflare does not start one
   automatically. Retrying the latest `main` deployment or pushing a small
   documentation change is sufficient.
6. Confirm the new production deployment is successful.
7. Confirm the `pages.dev` address shows the merged `main` version.

From this point onward:

- Pushing to a feature branch creates a preview.
- Opening a pull request gives a preview URL in GitHub.
- Merging into `main` automatically updates production.

## Phase 8: Add `arekbauer.com` to Cloudflare DNS

The domain is currently registered with Porkbun and uses Porkbun nameservers.
At the time this guide was written:

- `www.arekbauer.com` is a CNAME to the PythonAnywhere application.
- The root `arekbauer.com` uses Porkbun forwarding addresses.

Porkbun should remain the registrar. Only DNS hosting is moving.

### 8.1 Record the current DNS configuration

Before changing anything:

1. Sign in at <https://porkbun.com/account/domainsSpeedy>.
2. Find `arekbauer.com`.
3. Select **DNS** under the domain, or open
   **Details → DNS Records → Edit**.
4. Take screenshots or copy every displayed record into a private note.
5. Pay particular attention to MX and TXT records used for email, domain
   verification, SPF, DKIM, or DMARC. They must be preserved even though they
   are unrelated to the website.
6. If **Registry DNSSEC** is enabled at Porkbun, disable/remove the existing DS
   record before changing nameservers. DNSSEC can be enabled again through
   Cloudflare after the move is complete.

Do not delete the PythonAnywhere records at Porkbun yet.

### 8.2 Onboard the domain in Cloudflare

1. Return to <https://dash.cloudflare.com/>.
2. Open **Domains** and select **Onboard a domain** or **Add a domain**.
3. Enter only the apex domain: `arekbauer.com`. Do not enter `www`.
4. Let Cloudflare scan/import existing DNS records.
5. Select the **Free** plan.
6. Compare Cloudflare’s imported records with the private copy from Porkbun.
7. Manually add any missing MX, TXT, CNAME, or other records. The automatic
   scan is helpful but is not guaranteed to find everything.
8. Leave the existing PythonAnywhere `www` CNAME and current apex records in
   place in Cloudflare for this review step. They will be replaced when the
   Pages custom domains are attached.

Cloudflare will now display exactly two assigned nameservers. Keep that page
open. The names will be specific to this account; do not copy nameservers from
an example or another website.

### 8.3 Change the authoritative nameservers at Porkbun

Only do this after Cloudflare’s DNS record list is complete.

1. In Porkbun, return to **Domain Management**.
2. Find `arekbauer.com` and open **Details**.
3. Find **Nameservers** and select its edit icon.
4. Remove all four current `*.ns.porkbun.com` entries.
5. Enter the two nameservers assigned by Cloudflare, one per line.
6. Select **Save Nameservers** and then **Submit** if Porkbun asks for a second
   confirmation.
7. Return to Cloudflare and select **Check nameservers** if that option is
   shown.

The domain registration and renewal remain at Porkbun. Only DNS answers now
come from Cloudflare. Nameserver changes often appear within hours but can take
up to 48 hours worldwide. PythonAnywhere should stay running throughout this
period.

Wait until Cloudflare shows the domain status as **Active** before continuing.

## Phase 9: Attach the custom domains to Pages

Do this only after:

- The `main` deployment works at the `pages.dev` address.
- Cloudflare shows `arekbauer.com` as an active domain.
- The imported DNS records have been checked.

### 9.1 Attach `www`

1. Open **Workers & Pages → arekbauer-com**.
2. Open **Custom domains**.
3. Select **Set up a domain**.
4. Enter `www.arekbauer.com`.
5. Select **Continue** and confirm the proposed DNS change.
6. Cloudflare should replace the old PythonAnywhere `www` target with the
   Pages target automatically.
7. Wait until the hostname and certificate both show as active.
8. Open `https://www.arekbauer.com` in a private browser window and repeat the
   essential page and API checks.

### 9.2 Attach the apex domain

1. Still under **Custom domains**, select **Set up a domain** again.
2. Enter `arekbauer.com`.
3. Confirm the DNS change.
4. Wait until it is active.

Attaching the apex ensures Cloudflare has a valid proxied DNS target and TLS
certificate for the root domain. The next step redirects that hostname to the
canonical `www` version.

## Phase 10: Redirect the apex domain to `www`

The Astro configuration treats `https://www.arekbauer.com` as canonical, so
requests to the root domain should redirect there instead of serving a second
copy of the site.

1. In Cloudflare, select the `arekbauer.com` domain, not the Pages project.
2. Open **Rules → Overview**.
3. Select **Create rule → Redirect Rule**.
4. Name it `Redirect apex to www`.
5. Under **When incoming requests match**, choose **Wildcard pattern**.
6. For **Request URL**, enter:

   ```text
   http*://arekbauer.com/*
   ```

7. For **Target URL**, enter:

   ```text
   https://www.arekbauer.com/${1}
   ```

8. Set the status code to **301 Permanent Redirect**.
9. Enable **Preserve query string**.
10. Select **Deploy**.

Test all of these examples:

- `http://arekbauer.com`
- `https://arekbauer.com`
- `https://arekbauer.com/recipes/`
- A URL containing a query string

Each should keep its path/query where applicable and finish on the HTTPS `www`
hostname.

## Phase 11: Final Cloudflare settings

In the `arekbauer.com` domain settings:

1. Open **SSL/TLS → Edge Certificates**.
2. Turn on **Always Use HTTPS**.
3. Leave **Automatic HTTPS Rewrites** at its default unless a mixed-content
   problem is observed.
4. Do not enable HSTS during the migration. HSTS can be considered later after
   HTTPS has worked reliably for some time because an incorrect HSTS setup is
   harder to undo.
5. Return to **DNS → Records** and confirm the Pages-created `www` and apex
   records are proxied (orange cloud).
6. Re-enable DNSSEC from Cloudflare’s **DNS → Settings** only after the zone is
   active. Follow Cloudflare’s instructions to add the new DS details at
   Porkbun if required.

Optional settings such as Web Analytics can be enabled later. They are not
required for deployment. Do not enable Rocket Loader unless it is tested; it
can change JavaScript loading behaviour and this site does not need it.

## Phase 12: Observe before cancelling PythonAnywhere

Keep PythonAnywhere active for at least one normal day after the custom domain
switch. During that period, verify:

- The home page and every section work on desktop and mobile.
- The custom domain certificate remains valid.
- Several GitHub pushes deploy successfully.
- A pull request receives a separate preview deployment.
- Spotify updates normally throughout the day.
- The VCT and Pokémon endpoints return expected data.
- Any TRMNL device continues updating.
- Any domain email or verification service still works.

Take a final private backup of:

- The latest SQLite database.
- The complete media directory.
- Any values that exist only in PythonAnywhere configuration.

Only then cancel the PythonAnywhere subscription. The backup must not be added
to this public repository.

## Normal deployment workflow after migration

For ordinary content or design changes:

1. Create a branch.
2. Make the change locally.
3. Run:

   ```powershell
   npm test
   npm run build
   ```

4. Commit and push the branch.
5. Check the Cloudflare preview URL.
6. Merge the pull request into `main`.
7. Cloudflare automatically builds and publishes the live website.

No files need to be uploaded manually through the Cloudflare dashboard.

## Troubleshooting

### Build fails because of the Node version

Confirm that `NODE_VERSION` is set to `24` in both Production and Preview, then
retry the deployment.

### Cloudflare tries to install `requirements.txt` or Pillow

Cloudflare is building the old `main` branch or an old commit. The migration
branch no longer contains the legacy Python dependency manifest because the
deployed site does not use Django. Confirm that the deployment details show
`codex/cloudflare-migration`, then trigger a fresh deployment from that branch.

### npm reports `Missing script: "build"`

Cloudflare is building the old `main` branch instead of the Astro migration
branch. The old root `package.json` has a test script but no build script. Open
**Settings → Builds & deployments → Branch control**, set the production branch
to `codex/cloudflare-migration`, and save it. A retry of the old failed
deployment still uses the old commit, so trigger a fresh deployment from the
migration branch by pushing a new commit to it. Confirm the new deployment
details show both the migration branch and its latest commit before evaluating
the build log.

### The form asks for a deploy command or version command

This is the Workers Builds setup, not the Pages Git-integration setup. Do not
use `npx wrangler deploy` or `npx wrangler versions upload`. If the incorrect
application has already been created and has no custom domain, remove that
Cloudflare application, then create a new application from the **Pages** tab
and choose the Pages Git integration. A Pages Git build uploads the configured
`dist` output automatically and therefore has no deploy-command field.

### The site works but an API says configuration is missing

The relevant secret is absent from the environment serving that deployment.
Check **Settings → Variables and Secrets**, make sure it is encrypted and added
to both Production and Preview, and then create a new deployment.

### The domain still opens PythonAnywhere

Check, in order:

1. Cloudflare says the domain is active.
2. Porkbun lists only the two Cloudflare nameservers.
3. The Pages project shows the custom domain as active.
4. Cloudflare DNS no longer points `www` to PythonAnywhere.
5. Enough time has passed for nameserver and cached DNS changes to expire.

### Domain email stopped working

Compare Cloudflare’s DNS records with the Porkbun screenshots. Restore any
missing MX, TXT, SPF, DKIM, or DMARC records using the exact values supplied by
the email provider.

### A custom domain reports a certificate or validation error

Wait for the domain to become active first. If CAA records exist, ensure they
allow one of Cloudflare’s certificate authorities. Do not repeatedly delete
and recreate the domain while certificate validation is pending.

### A preview branch is not deploying

Check **Settings → Builds & deployments → Branch control** and ensure preview
deployments are set to **All non-production branches**.

## Official references

- [Create a Cloudflare account](https://developers.cloudflare.com/fundamentals/account/create-account/)
- [Enable Cloudflare two-factor authentication](https://developers.cloudflare.com/fundamentals/user-profiles/2fa/)
- [Cloudflare Pages Git integration](https://developers.cloudflare.com/pages/get-started/git-integration/)
- [Astro on Cloudflare Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-an-astro-site/)
- [Pages environment variables and secrets](https://developers.cloudflare.com/pages/functions/bindings/)
- [Pages branch deployment controls](https://developers.cloudflare.com/pages/configuration/branch-build-controls/)
- [Pages preview deployments](https://developers.cloudflare.com/pages/configuration/preview-deployments/)
- [Add a domain to Cloudflare DNS](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/)
- [Cloudflare Pages custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Create a Cloudflare redirect rule](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/create-dashboard/)
- [Change nameservers at Porkbun](https://kb.porkbun.com/article/22-how-to-change-nameservers)
