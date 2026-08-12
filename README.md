# SteadiDay Website

Marketing and informational site for the [SteadiDay iOS app](https://github.com/SCM-Solutions-LLC/steadiday-app). Deployed at [steadiday.com](https://steadiday.com) via GitHub Pages.

## What's in this repo

| Path | Purpose |
|------|---------|
| `index.html` | Main landing page |
| `preview.html` | App preview page |
| `blog/` | Blog posts |
| `assets/` | Images, icons, screenshots |
| `scripts/` | Python utilities (sitemap generation, blog tooling) |
| `privacy.html` | Privacy policy |
| `terms.html` | Terms of service |
| `security.html` | Security policy |
| `data-breach.html` | Data breach policy |
| `data-retention.html` | Data retention policy |
| `liability.html` | Liability disclaimer |
| `sitemap.xml` | SEO sitemap |
| `robots.txt` | Crawler directives |
| `CNAME` | Custom domain config (`steadiday.com`) |
| `.github/workflows/` | GitHub Actions for automated deployment |

## Local development

No build step required. Open `index.html` directly in a browser, or run a local server:

```bash
python3 -m http.server 8000
# → http://localhost:8000
```

## Checks

The same three checks CI runs on every pull request, runnable locally:

```bash
scripts/audit.sh                      # accessibility: contrast, axe-core, keyboard pass
python3 scripts/check_pricing_sync.py # homepage prices match pricing.html
python3 scripts/check_blog_consistency.py  # posts match the generator template
```

`scripts/audit.sh` installs its two npm dependencies on first run, serves the
site, and audits every page. Pass filenames to narrow it:

```bash
scripts/audit.sh index.html pricing.html
```

## Deployment

Pushes to `main` deploy automatically via GitHub Actions to GitHub Pages. The `CNAME` file routes traffic from `scm-solutions-llc.github.io/steadiday` to `steadiday.com`.

To update the sitemap after adding pages:

```bash
python3 scripts/generate_sitemap.py
```

## Adding a blog post

`scripts/generate_blog.py` owns the post template — hand-written posts drift
from it and `check_blog_consistency.py` will fail the build.

1. Add the post to `scripts/generate_blog.py` and run it
2. Add the entry to the blog index in `index.html`
3. Regenerate `sitemap.xml`
4. Push to `main`

Template changes belong in the generator, then get backfilled across existing
posts with `scripts/backfill_blog_a11y.py`.

## SEO / Search verification

- `BingSiteAuth.xml` — Bing Webmaster Tools verification
- `c5526cc077704889a3a171a6c73eb636.txt` — Google Search Console verification
- `robots.txt` — allows all crawlers, points to sitemap

## ⚠️ Security note

`GoogleService-Info.plist` should not be committed to this public repo. Add it to `.gitignore` and remove it from history:

```bash
echo "GoogleService-Info.plist" >> .gitignore
git rm --cached GoogleService-Info.plist
git commit -m "Remove GoogleService-Info.plist from tracking"
git push
```

Then rotate the affected Firebase API keys at [console.firebase.google.com](https://console.firebase.google.com).

## Related

- **App code:** [SCM-Solutions-LLC/steadiday-app](https://github.com/SCM-Solutions-LLC/steadiday-app)
- **App Store listing:** [SteadiDay on the App Store](https://apps.apple.com)
- **LinkedIn:** [SteadiDay company page](https://linkedin.com/company/steadiday)
