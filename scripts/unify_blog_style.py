#!/usr/bin/env python3
"""Unify blog post styling on the SteadiDay brand look.

Posts shipped in two generations:

  brand look    Poppins headings, sage accent - matches the marketing site
  editorial     Merriweather headings, teal #1A8A7D accent - a different hue
                (173 deg vs the brand's 158 deg) and a different typeface

31 of 38 posts already use the brand look, so this migrates the remainder and
points the generator at the same source of truth. Both variants use an
identical class vocabulary, so only the <style> block and the Google Fonts
link change - no markup is touched.

The reference post supplies the canonical CSS, which keeps this in step with
the accessibility fixes already applied to those posts.

Safe to re-run: posts already on the brand look are left alone.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
GENERATOR = ROOT / "scripts" / "generate_blog.py"

# Any post already on the brand look works as the reference.
REFERENCE = BLOG / "2026-03-21-foods-that-fight-joint-pain.html"

FONTS_RE = re.compile(r'<link href="https://fonts\.googleapis\.com/css2[^>]*>')
STYLE_RE = re.compile(r"<style>.*?</style>", re.DOTALL)

# Present only in the editorial variant.
EDITORIAL_MARKERS = ("Merriweather", "--teal:")


def canonical_parts():
    ref = REFERENCE.read_text(encoding="utf-8")
    fonts = FONTS_RE.search(ref)
    style = STYLE_RE.search(ref)
    if not fonts or not style:
        raise SystemExit(f"reference post {REFERENCE.name} is missing fonts link or style block")
    return fonts.group(0), style.group(0)


def migrate_posts(fonts, style):
    posts = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html")
    migrated = []
    for path in posts:
        html = path.read_text(encoding="utf-8")
        if not any(m in html for m in EDITORIAL_MARKERS):
            continue  # already on the brand look
        html = FONTS_RE.sub(lambda _: fonts, html, count=1)
        html = STYLE_RE.sub(lambda _: style, html, count=1)
        path.write_text(html, encoding="utf-8")
        migrated.append(path.name)
    return migrated


def update_generator(fonts, style):
    """Point the template at the same CSS. Braces are doubled because the
    template is rendered with str.format()."""
    src = GENERATOR.read_text(encoding="utf-8")
    if "Merriweather" not in src:
        return False

    escaped_style = style.replace("{", "{{").replace("}", "}}")
    src = FONTS_RE.sub(lambda _: fonts, src, count=1)
    src = STYLE_RE.sub(lambda _: escaped_style, src, count=1)
    GENERATOR.write_text(src, encoding="utf-8")
    return True


def main():
    fonts, style = canonical_parts()
    print(f"reference: {REFERENCE.name} ({len(style)} chars of CSS)")

    migrated = migrate_posts(fonts, style)
    print(f"posts migrated to brand look: {len(migrated)}")
    for name in migrated:
        print(f"  {name}")

    print("generator updated" if update_generator(fonts, style)
          else "generator already on brand look")
    return 0


if __name__ == "__main__":
    sys.exit(main())
