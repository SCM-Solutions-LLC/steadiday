#!/usr/bin/env python3
"""Fail if blog posts drift from the brand look or lose their a11y invariants.

scripts/generate_blog.py is the source of truth for post markup and CSS. A post
edited by hand will be silently reverted the next time the generator runs, and
a change made only to a post never reaches future posts. This check keeps both
directions honest.

It also guards the generator template itself, because that is the failure that
actually costs something: if the template loses an invariant, every future post
is born broken.

History this is guarding against:
  * 7 posts shipped without the shared stylesheet, so they had no focus rings
  * 30 of 38 posts rendered an off-brand teal accent (hue 173 vs the brand 158)
  * no post had a skip link or a <main> landmark until #32

Exits non-zero on drift.
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
GENERATOR = ROOT / "scripts" / "generate_blog.py"

# (label, must be present, must be absent)
POST_RULES = [
    ("skip link", 'class="skip-link"', None),
    ("main landmark", '<main id="main">', None),
    ("shared stylesheet", "steadiday-shared.css", None),
    ("brand heading font", "Poppins", None),
    ("no off-brand teal token", None, "--teal:"),
    ("no serif heading font", None, "Merriweather"),
    ("decorative hero alt", 'alt="" class="hero-image"', None),
]

# The generator emits the same markup with placeholders, so the hero rule is
# checked separately against its template form.
TEMPLATE_RULES = [r for r in POST_RULES if r[0] != "decorative hero alt"] + [
    ("decorative hero alt", 'alt="" class="hero-image"', None),
]


def check(html, rules, label):
    problems = []
    for name, required, forbidden in rules:
        if required and required not in html:
            problems.append(f"missing {name}")
        if forbidden and forbidden in html:
            problems.append(f"has {name.replace('no ', '')} ({forbidden})")
    return problems


def main():
    if not BLOG.is_dir():
        print("FAILED: blog/ directory not found")
        return 1

    posts = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html")
    if not posts:
        print("FAILED: no blog posts found")
        return 1

    failed = {}
    for path in posts:
        problems = check(path.read_text(encoding="utf-8"), POST_RULES, path.name)
        if problems:
            failed[path.name] = problems

    # blog/index.html is a listing page, not a post: it has no hero image and
    # no article typography, so only the structural invariants apply.
    index = BLOG / "index.html"
    if index.exists():
        html = index.read_text(encoding="utf-8")
        problems = []
        if 'class="skip-link"' not in html:
            problems.append("missing skip link")
        if 'id="main"' not in html:
            problems.append("missing main landmark")
        if problems:
            failed["index.html"] = problems

    # The template matters most: it decides what every future post looks like.
    template_problems = []
    if GENERATOR.exists():
        src = GENERATOR.read_text(encoding="utf-8")
        m = re.search(r"def get_html_template\(\):\s*\n\s*return '''(.*?)'''", src, re.DOTALL)
        if not m:
            template_problems.append("could not locate the template literal")
        else:
            template_problems = check(m.group(1), TEMPLATE_RULES, "template")
    else:
        template_problems.append("scripts/generate_blog.py not found")

    print(f"checked {len(posts)} post(s) + blog/index.html + the generator template")

    if failed or template_problems:
        print("\nFAILED:")
        if template_problems:
            print("  scripts/generate_blog.py (template — affects every future post):")
            for p in template_problems:
                print(f"    - {p}")
        for name, problems in sorted(failed.items()):
            print(f"  blog/{name}:")
            for p in problems:
                print(f"    - {p}")
        print("\nRun scripts/unify_blog_style.py and scripts/backfill_blog_a11y.py to repair,")
        print("and fix the template so new posts are generated correctly.")
        return 1

    print("PASSED: every post and the generator template are on the brand look")
    return 0


if __name__ == "__main__":
    sys.exit(main())
