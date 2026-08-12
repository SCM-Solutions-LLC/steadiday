#!/usr/bin/env python3
"""Apply the site's standard accessibility fixes to top-level pages.

The legal and policy pages (security, privacy, terms, liability, data
retention, data breach) were never part of the earlier accessibility passes,
and the audit found the same three failure classes there that were fixed on
the marketing pages and blog:

  * --sage #4A9D7E used as text            3.18:1 - 3.27:1  (needs 4.5:1)
  * --sage used as a fill under white text 3.27:1
  * 50%-opacity white footer copyright     4.46:1

They all already carry a <main> landmark and link the shared stylesheet, so
they only need the colour fixes and a skip link.

The transforms are shared with scripts/backfill_blog_a11y.py so both surfaces
stay on one definition of "fixed".

Safe to re-run: every step checks for its own marker first.
"""

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Top-level pages that are not the marketing homepage (already handled) and
# have a <nav> immediately inside <body>.
PAGES = [
    "security.html",
    "privacy.html",
    "terms.html",
    "liability.html",
    "data-retention.html",
    "data-breach.html",
]

SKIP_LINK = '    <a class="skip-link" href="#main">Skip to main content</a>\n'


def _blog_module():
    """Reuse the colour transforms rather than restating them."""
    spec = importlib.util.spec_from_file_location(
        "backfill_blog_a11y", ROOT / "scripts" / "backfill_blog_a11y.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def add_skip_link(html):
    if 'class="skip-link"' in html:
        return html, False
    if "<body>\n" not in html:
        return html, False
    return html.replace("<body>\n", "<body>\n" + SKIP_LINK, 1), True


def label_main(html):
    """The skip link needs a target."""
    if '<main id="main"' in html or 'id="main"' in html:
        return html, False
    for opening in ("<main>", '<main class="'):
        if opening in html:
            replacement = ('<main id="main">' if opening == "<main>"
                           else '<main id="main" class="')
            return html.replace(opening, replacement, 1), True
    return html, False


def main():
    blog = _blog_module()
    steps = [
        ("sage text", blog.fix_sage_palette),
        ("sage fills", blog.fix_sage_fills),
        ("faint text", blog.fix_faint_text),
        ("skip link", add_skip_link),
        ("main id", label_main),
    ]

    touched = 0
    for name in PAGES:
        path = ROOT / name
        if not path.exists():
            print(f"  {name}: missing, skipped")
            continue
        html = original = path.read_text(encoding="utf-8")
        applied = []
        for label, fn in steps:
            html, changed = fn(html)
            if changed:
                applied.append(label)
        if html != original:
            path.write_text(html, encoding="utf-8")
            touched += 1
            print(f"  {name}: {', '.join(applied)}")
        else:
            print(f"  {name}: already up to date")

    print(f"{touched}/{len(PAGES)} pages updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
