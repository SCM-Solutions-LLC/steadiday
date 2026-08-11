#!/usr/bin/env python3
"""Backfill accessibility fixes across generated blog posts.

Posts exist in two template generations:

  sage variant  - links ../steadiday-shared.css, uses var(--sage) for link text
  teal variant  - self-contained palette, uses var(--teal) for link text

Both shipped link colours that fail WCAG AA (sage 3.27:1, teal 4.22:1), and
neither had a skip link or a <main> landmark. This script brings both up to
the same standard as the marketing pages.

Safe to run repeatedly - every edit checks for its own marker first.
"""

import pathlib
import re
import sys

BLOG = pathlib.Path(__file__).resolve().parent.parent / "blog"

SHARED_CSS_LINK = '<link rel="stylesheet" href="../steadiday-shared.css">'
SKIP_LINK = '    <a class="skip-link" href="#main">Skip to main content</a>\n'

# AA-safe teal on the same hue/saturation as the original brand teal.
TEAL_TOKENS = "--teal-text:#157065;--teal-deep:#10564E;"


def add_shared_css(html):
    """The shared stylesheet supplies focus rings, skip-link styling and the
    reduced-motion block. The teal variant never linked it."""
    if "steadiday-shared.css" in html:
        return html, False
    m = re.search(r'( *<link href="https://fonts\.googleapis\.com/css2[^>]*>\n)', html)
    if not m:
        return html, False
    return html.replace(m.group(1), m.group(1) + "    " + SHARED_CSS_LINK + "\n", 1), True


def fix_teal_palette(html):
    """teal #1A8A7D is 4.22:1 on white - demote it to a fill-only colour."""
    changed = False
    if "--teal:#1A8A7D" in html and "--teal-text:" not in html:
        html = html.replace("--teal:#1A8A7D;", "--teal:#1A8A7D;" + TEAL_TOKENS, 1)
        changed = True
    for old, new in [
        ("a{color:var(--teal);", "a{color:var(--teal-text);"),
        ("a:hover{color:var(--teal-dark);", "a:hover{color:var(--teal-deep);"),
        ("background:var(--white);color:var(--teal);", "background:var(--white);color:var(--teal-text);"),
        # 90%-opacity white on the old gradient start measured 3.73:1
        ("linear-gradient(135deg,var(--teal) 0%,var(--teal-dark) 100%)",
         "linear-gradient(135deg,var(--teal-text) 0%,var(--teal-deep) 100%)"),
    ]:
        if old in html:
            html = html.replace(old, new)
            changed = True
    return html, changed


def fix_sage_palette(html):
    """sage #4A9D7E is 3.27:1 on white; --color-brand-text is 5.01:1."""
    changed = False
    pattern = re.compile(r"(?<![-\w])color: *var\(--sage\)")
    html, n = pattern.subn("color: var(--color-brand-text)", html)
    changed |= bool(n)
    pattern = re.compile(r"(?<![-\w])color: *var\(--sage-dark\)")
    html, n = pattern.subn("color: var(--color-brand-hover)", html)
    changed |= bool(n)
    return html, changed


def fix_sage_fills(html):
    """sage #4A9D7E is 3.27:1, so white text sitting on a sage fill fails too.
    --color-brand-text is the same hue, dark enough to carry white text."""
    changed = False
    for old, new in [
        # CTA panel gradient: 90%-opacity white on it measured 2.95:1
        ("linear-gradient(135deg, var(--sage) 0%, var(--sage-dark) 100%)",
         "linear-gradient(135deg, var(--color-brand-text) 0%, var(--color-brand-hover) 100%)"),
        ("linear-gradient(135deg,var(--sage) 0%,var(--sage-dark) 100%)",
         "linear-gradient(135deg,var(--color-brand-text) 0%,var(--color-brand-hover) 100%)"),
    ]:
        if old in html:
            html = html.replace(old, new)
            changed = True

    # Solid sage fills whose rule also sets white text
    def fix_rule(m):
        nonlocal changed
        sel, body = m.group(1), m.group(2)
        if not re.search(r"background(-color)?: *var\(--sage\)", body):
            return m.group(0)
        if not re.search(r"color: *(white|#fff|#FFF|var\(--white\)|rgba?\(255)", body):
            return m.group(0)
        changed = True
        return sel + "{" + re.sub(r"background(-color)?: *var\(--sage\)",
                                  r"background\1: var(--color-brand-text)", body) + "}"

    html = re.sub(r"([^{}]+)\{([^{}]*)\}", fix_rule, html)
    return html, changed


def fix_faint_text(html):
    """Semi-transparent white text that lands under 4.5:1 once composited.

    50% white on the dark footer is 4.46:1; 90% white on the CTA panel is
    4.41:1. Both are a hair under, so raise the alpha rather than restyle.
    Whitespace inside the rgba() varies between template generations.
    """
    changed = False
    # footer copyright
    new, n = re.subn(r"color: *rgba\(255, *255, *255, *0\.5\)", "color: rgba(255, 255, 255, 0.7)", html)
    changed |= bool(n)
    # CTA panel body copy
    new, n = re.subn(r"color: *rgba\(255, *255, *255, *0\.9\)( *!important)?",
                     r"color: rgba(255, 255, 255, 1)\1", new)
    changed |= bool(n)
    return new, changed


def fix_gold_rating(html):
    """Gold #D4A853 star ratings are 2.14:1 on cream - they are text, not
    decoration, so they need to be readable."""
    old = ".rating {\n            color: var(--gold);"
    if old not in html:
        return html, False
    return html.replace(old, ".rating {\n            color: #8A6412;"), True


def add_skip_link(html):
    if 'class="skip-link"' in html:
        return html, False
    return html.replace("<body>\n", "<body>\n" + SKIP_LINK, 1), True


def add_main_landmark(html):
    """Wrap hero image through back-to-blog. Nav and breadcrumbs stay outside."""
    if '<main id="main">' in html:
        return html, False
    hero = re.search(r'( *<img src="[^"]*" alt="[^"]*" class="hero-image"[^>]*>\n)', html)
    if not hero:
        return html, False
    # One hand-written post uses a bare <footer> rather than the generated
    # <footer class="footer">.
    tail = next((t for t in ('    <footer class="footer">', '    <footer>') if t in html), None)
    if not tail:
        return html, False
    html = html.replace(hero.group(1), '    <main id="main">\n' + hero.group(1), 1)
    return html.replace(tail, "    </main>\n" + tail, 1), True


def blank_hero_alt(html):
    """The hero image repeats the <h1> immediately below it, so alt text made
    screen readers announce the headline twice. Decorative -> empty alt."""
    # Single-quoted replacement: a raw double-quoted one would emit a literal
    # backslash before each quote.
    new = re.sub(r'(<img src="[^"]*") alt="[^"]*"( class="hero-image")', r'\1 alt=""\2', html)
    # Repair posts written by the earlier buggy pass.
    new = new.replace(r'alt=\"\" class="hero-image"', 'alt="" class="hero-image"')
    return new, new != html


# blank_hero_alt runs before add_main_landmark: the landmark is anchored on the
# hero <img> tag, so the alt attribute must be well-formed first.
STEPS = [add_shared_css, fix_teal_palette, fix_sage_palette, fix_sage_fills,
         fix_faint_text, fix_gold_rating,
         add_skip_link, blank_hero_alt, add_main_landmark]


def main():
    posts = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html")
    if not posts:
        print("no posts found", file=sys.stderr)
        return 1

    touched = 0
    tally = {fn.__name__: 0 for fn in STEPS}
    for path in posts:
        html = original = path.read_text(encoding="utf-8")
        for fn in STEPS:
            html, changed = fn(html)
            tally[fn.__name__] += int(changed)
        if html != original:
            path.write_text(html, encoding="utf-8")
            touched += 1

    print(f"{touched}/{len(posts)} posts updated")
    for name, count in tally.items():
        print(f"  {name:20} {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
