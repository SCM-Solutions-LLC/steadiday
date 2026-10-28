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
| `steadiday-assistant.css` | Styles for the on-page assistant |
| `steadiday-assistant.js` | On-page assistant: knowledge base + search |
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
python3 scripts/check_pricing_sync.py # homepage + assistant prices match pricing.html
python3 scripts/check_blog_consistency.py  # posts match the generator template
python3 scripts/inject_assistant.py --check  # every page carries the assistant
```

`scripts/audit.sh` installs its two npm dependencies on first run, serves the
site, and audits every page. Pass filenames to narrow it:

```bash
scripts/audit.sh index.html pricing.html
```

## The on-page assistant

Every page carries a floating **Ask a question** button. It opens a panel that
searches a knowledge base compiled into `steadiday-assistant.js` and answers
with text lifted from a real page, plus a link to it.

There is no backend and no network call. This site is static, so an API key
shipped to the browser would be a key anyone could spend — the assistant
searches locally instead. That also means it cannot invent an answer: it either
finds one in the knowledge base or says it did not.

Scope is the product only — plans, features, accounts, privacy, setup. Health
questions are routed to the blog and to a doctor rather than answered, which is
deliberate given who this site is written for.

**To add or change an answer**, edit the `KB` array at the top of
`steadiday-assistant.js`. Each entry needs:

| Field | Purpose |
|-------|---------|
| `q` | The canonical question, shown as the card heading |
| `keys` | The words people actually type — synonyms and common phrasings |
| `a` | The answer, which should match what the linked page says |
| `link` / `linkText` | Where to read more. Written as if from the site root; blog pages get the `../` hop at runtime |

Keep `a` in step with the page it links to. An answer that drifts from the page
is worse than no answer.

**To add the assistant to a new page**, run the injector — it is idempotent, so
running it over the whole site is safe:

```bash
python3 scripts/inject_assistant.py           # add it wherever it is missing
python3 scripts/inject_assistant.py --check   # report, change nothing
```

New blog posts get it automatically: the references are part of the template in
`scripts/generate_blog.py`.

Queries are reported to Google Analytics as an `assistant_query` event with the
search term and the number of results. The ones returning zero results are the
useful ones — they are the questions the site does not currently answer.

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
