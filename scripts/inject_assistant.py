#!/usr/bin/env python3
"""Add the on-page assistant to every page on the site.

The assistant is two files — steadiday-assistant.css and
steadiday-assistant.js — and it needs to be reachable from anywhere a
visitor might land, which is all 65 pages including the 57 blog posts.
Hand-editing that many files is how pages drift, so this owns the edit
instead.

Two insertions per page:

  * the stylesheet, immediately after the shared stylesheet, so it
    inherits the design tokens it is built from and nothing else has to
    change about load order
  * the script, deferred, immediately before </body>

Paths are taken from the shared stylesheet link already on the page
rather than guessed, so blog posts keep their ../ hop and top-level
pages stay relative.

The widget itself is built by JS at runtime. Nothing is injected into
the markup beyond those two references, so with JS disabled the page is
exactly as it was and there is no dead button to click.

Safe to re-run: each step looks for its own reference first.

    python3 scripts/inject_assistant.py            # all pages
    python3 scripts/inject_assistant.py --check    # report, change nothing
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS_NAME = "steadiday-assistant.css"
JS_NAME = "steadiday-assistant.js"

# Matches the shared stylesheet link and captures its indentation and the
# relative prefix ("" at the root, "../" inside blog/).
SHARED_CSS = re.compile(
    r'^([ \t]*)<link rel="stylesheet" href="((?:\.\./)*)steadiday-shared\.css">',
    re.MULTILINE,
)


def pages():
    """Every page that links the shared stylesheet, which is all of them."""
    found = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html"))
    return [p for p in found if "steadiday-shared.css" in p.read_text(encoding="utf-8")]


def add_stylesheet(html):
    if CSS_NAME in html:
        return html, False
    match = SHARED_CSS.search(html)
    if not match:
        return html, False
    indent, prefix = match.group(1), match.group(2)
    link = f'\n{indent}<link rel="stylesheet" href="{prefix}{CSS_NAME}">'
    return html[: match.end()] + link + html[match.end() :], True


def add_script(html):
    if JS_NAME in html:
        return html, False
    match = SHARED_CSS.search(html)
    if not match:
        return html, False
    prefix = match.group(2)
    tag = f'<script src="{prefix}{JS_NAME}" defer></script>\n'

    # Match the indentation of the closing </body> so the tag sits with
    # the markup around it rather than hard against the margin.
    body_close = re.search(r"^([ \t]*)</body>", html, re.MULTILINE)
    if not body_close:
        return html, False
    indent = body_close.group(1)
    insert_at = body_close.start()
    return html[:insert_at] + indent + tag + html[insert_at:], True


def main():
    check_only = "--check" in sys.argv
    targets = pages()
    if not targets:
        print("no pages link steadiday-shared.css — nothing to do", file=sys.stderr)
        return 1

    changed = []
    skipped = []
    failed = []

    for path in targets:
        html = path.read_text(encoding="utf-8")
        html, css_added = add_stylesheet(html)
        html, js_added = add_script(html)

        if CSS_NAME not in html or JS_NAME not in html:
            failed.append(path)
            continue

        if css_added or js_added:
            changed.append(path)
            if not check_only:
                path.write_text(html, encoding="utf-8")
        else:
            skipped.append(path)

    verb = "would update" if check_only else "updated"
    label = "would add" if check_only else "wrote"
    print(f"{verb} {len(changed)} page(s); {len(skipped)} already had it")
    for path in changed:
        print(f"  {label}: {path.relative_to(ROOT)}")
    if failed:
        print(f"\ncould not place both references on {len(failed)} page(s):", file=sys.stderr)
        for path in failed:
            print(f"  {path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
