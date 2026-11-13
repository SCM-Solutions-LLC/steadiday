#!/usr/bin/env python3
"""Fail if a site page links to a page, file or #anchor on this site that does not exist.

Covers every href/src in every published *.html page (any folder except the
Jekyll `exclude:` list in _config.yml and dot/underscore folders) that points
at this site: relative paths, root-relative paths, and absolute steadiday.com URLs.
External sites are not checked, so the result never depends on third-party uptime.

History this is guarding against:
  * generated posts linked to WordPress-style URLs that never existed on this
    static site (/blog/<slug>/ instead of blog/YYYY-MM-DD-slug.html): the
    sodium link fixed in #81 and the gut-health and fall-vaccine links in #82

Exits non-zero on any broken link.
"""

import html
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
SITE_HOSTS = {"steadiday.com", "www.steadiday.com"}
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}

_ids = {}


def anchors(path):
    if path not in _ids:
        text = path.read_text(encoding="utf-8", errors="replace")
        _ids[path] = set(re.findall(r'\b(?:id|name)="([^"]+)"', text))
    return _ids[path]


def problem(page, url):
    """Return why `url` on `page` is broken, or None if it is fine or not ours."""
    u = urlsplit(html.unescape(url))
    if u.scheme in SKIP_SCHEMES or (u.netloc and u.netloc.lower() not in SITE_HOSTS):
        return None
    path = unquote(u.path)
    if not path:
        target = page
    elif u.netloc or path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = (page.parent / path).resolve()
    if target.is_dir():
        target = target / "index.html"
    if not target.exists():
        return "no such file"
    if u.fragment and target.suffix == ".html" and u.fragment not in anchors(target):
        return f"no #{u.fragment} on that page"
    return None


def site_pages():
    """Every *.html GitHub Pages publishes; mirrors Jekyll's default and _config.yml excludes."""
    config = (ROOT / "_config.yml").read_text(encoding="utf-8")
    excluded = {e.strip("/") for e in re.findall(r"^\s+-\s+(\S+)", config, re.M)} | {"node_modules"}
    return sorted(
        p for p in ROOT.rglob("*.html")
        if not any(part in excluded or part[0] in "._" for part in p.relative_to(ROOT).parts[:-1])
    )


def self_check():
    page = BLOG / "index.html"
    assert problem(page, "https://steadiday.com/blog/no-such-slug-here/") == "no such file"
    assert problem(page, "#definitely-not-an-anchor-id") is not None
    assert problem(page, "https://example.com/missing") is None
    assert problem(page, "mailto:someone@example.com") is None
    found = site_pages()
    assert ROOT / "index.html" in found and page in found
    assert not any(".git" in p.parts or "promo-video" in p.parts for p in found)


def main():
    self_check()
    pages = site_pages()
    broken = []
    for page in pages:
        lines = page.read_text(encoding="utf-8", errors="replace").splitlines()
        for n, line in enumerate(lines, 1):
            for url in re.findall(r'\b(?:href|src)="([^"]*)"', line):
                why = problem(page, url)
                if why:
                    broken.append(f"  {page.relative_to(ROOT)}:{n}  {url}  ({why})")

    print(f"checked internal links in {len(pages)} page(s)")
    if broken:
        print("\nFAILED: broken internal links:")
        print("\n".join(broken))
        print("\nPoint each one at the real file (blog posts are blog/YYYY-MM-DD-slug.html), or unlink it.")
        return 1
    print("PASSED: every internal link resolves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
